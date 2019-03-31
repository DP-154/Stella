from collections import namedtuple
import json
import requests
import os
from database.db_connection import session_maker
from database.queries import session_scope, update_image
from database.models import GasStation, FuelCompany
from database.db_store_data_bot import db_store_start
# from processor.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from processor.image_recognition import digit_to_price
from processor.gas_price_detection import YukonDetect
from processor.gas_price_detection import BrsmDetect
from transport.data_provider import DropBoxDataProvider

TMP_IS_PREMIUM = False
TMP_IS_RECOGNIZED = True
TMP_IS_FROM_METADATA = False

dbx_token = os.environ['DROPBOX_TOKEN']
telegram_token = os.environ['TELEGRAM_TOKEN']


def comany_and_address(lat, long):
    # md = MetaDataFromCoordinates(lat, long)
    # return md.get_name(), md.get_address()
    with session_scope() as session:
        fc = session.query(FuelCompany).first()
        gs = (session.query(GasStation)
              .filter(GasStation.fuel_company_connection == fc)
              .first())

        return fc.fuel_company_name, gs.address


def store_bot_data(telegram_id, image_link, image_path, company_name, address):
    # TODO maybe refactor with 1 argument - dict?
    # TODO put in database GPS coordinates
    session = session_maker()
    stored_data = db_store_start(session, telegram_id, image_path, company_name, address)
    recognition_tuple = get_recognition_tuple(company_name, image_link)
    if isinstance(recognition_tuple[0], bool):
        count_tuple = 1
    else:
        count_tuple = len(recognition_tuple)


    res_str = ''
    recognition_result = namedtuple('rec_result', ['is_recognized', 'fuel_type', 'price'])
    location_result = namedtuple('loc_result', ['gas_station', 'is_from_metadata'])
    for row in range(count_tuple):
        if count_tuple == 1:
            is_recognized, rec_fuel_type, price = recognition_tuple
        else:
            is_recognized, rec_fuel_type, price = recognition_tuple[row]
        if is_recognized:
            if price.replace('.', '', 1).isdigit():
                rec_price = float(price)
                rr = recognition_result(is_recognized, rec_fuel_type, rec_price)
                lr = location_result(stored_data.gas_station, TMP_IS_FROM_METADATA)
                try:
                    update_image(session, stored_data.image, rr, lr)
                except RuntimeError:
                    res_str = res_str+f"there isn't a fuel {rec_fuel_type} \n"
                else:
                    res_str = res_str + f'A{rec_fuel_type}: {price} uah \n'
            else:
                res_str = res_str+f'{price} is not a float number \n'
        else:
            res_str = res_str+'string is not recognized \n'
    session.close()
    return res_str


def get_telegram_upload_image_paths(file_id):
    tg_file_link = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
    tg_file = requests.get(tg_file_link)
    loaded_data = json.loads(tg_file.text)
    file_path = loaded_data["result"]["file_path"]

    tg_down_path = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
    dirname, basename = os.path.split(file_path)
    dbx_path = "/telegram_files/" + basename
    return tg_down_path, dbx_path


def upload_image_to_dbx(file_path, dbx_path):
    dbx_provider = DropBoxDataProvider(dbx_token)
    dbx_path = dbx_provider.file_upload(file_path, dbx_path)
    return dbx_path, dbx_provider.get_file_tmp_link(dbx_path)


def get_recognition_class(company_name):
    company_dict = {('yukon', 'юкон'): YukonDetect, ('brsm', 'брсм'): BrsmDetect}
    for comp_dict_names in company_dict.keys():
        for name in comp_dict_names:
            if company_name.strip().lower().find(name) > -1:
                return company_dict[comp_dict_names]


def get_recognition_tuple(company_name, image_link):
    recognition_class = get_recognition_class(company_name)
    if recognition_class is None:
        return digit_to_price(image_link)
    else:
        return recognition_class(image_link).digit_to_price()
