from collections import namedtuple
import json
import requests
import os
from database.db_connection import session_maker
from database.queries import session_scope, update_image
from database.models import GasStation, FuelCompany
from database.db_store_data_bot import db_store_start, db_get_fuel, db_store_recognized
# from processor.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from processor.image_recognition import digit_to_price
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


def store_bot_data(telegram_id, image_link, company_name, address, lat, lng):
    # TODO maybe refactor with 1 argument - dict?
    # TODO put in database GPS coordinates

    is_recognized, rec_fuel_type, price = digit_to_price(image_link)

    session = session_maker()
    stored_data = db_store_start(session, telegram_id, image_link, company_name, address)

    if is_recognized:
        is_premium = TMP_IS_PREMIUM
        fuel = db_get_fuel(session, rec_fuel_type, is_premium)
        if fuel is None:
            return "There isn't a fuel {} in database".format(rec_fuel_type)

        if price.replace('.', '', 1).isdigit():
            rec_price = float(price)
            recognition_result = namedtuple('rec_result', ['is_recognized', 'fuel_type', 'price'])
            rr = recognition_result(is_recognized, rec_fuel_type, rec_price)

            location_result = namedtuple('loc_result', ['gas_station', 'is_from_metadata'])
            lr = location_result(stored_data['gas_station'], TMP_IS_FROM_METADATA)
            update_image(session, stored_data['image'], rr, lr)
        else:
            return "{} is not a float number".format(price)
    else:
        return 'photo is not recognized'
    session.close()
    return f'Ok! \nA{rec_fuel_type}: {price} грн'


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
    return dbx_provider.get_file_tmp_link(dbx_path)
