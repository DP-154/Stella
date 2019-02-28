from collections import namedtuple

from database.db_connection import session_maker
from database.queries import session_scope, update_image
from database.models import GasStation, FuelCompany
from database.db_store_data_bot import db_store_start, db_get_fuel, db_store_recognized
#from stella_api.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from stella_api.image_recognition import digit_to_price

TMP_IS_PREMIUM = False
TMP_IS_RECOGNIZED = True
TMP_IS_FROM_METADATA = False

url = 'https://api.telegram.org/file/bot722747893:AAFSkHEIgGW7xP01lRpNjVgnkF-Dk_8b5Rg/documents/file_25.png'


def comany_and_address(lat, long):
    #md = MetaDataFromCoordinates(lat, long)
    #return md.get_name(), md.get_address()
    with session_scope() as session:
        fc = session.query(FuelCompany).first()
        gs = (session.query(GasStation)
              .filter(GasStation.fuel_company_connection == fc)
              .first())

        return fc.fuel_company_name, gs.address
        


def store_bot_data(tg_id, image_link, latitude, longitude):
    #md_from_coordinates = MetaDataFromCoordinates(latitude, longitude)
    #company_name = md_from_coordinates.get_name()
    #address = md_from_coordinates.get_address()

    company_name, address = comany_and_address(latitude, longitude)
    
    session = session_maker()
    stored_data = db_store_start(session, tg_id, image_link, company_name, address)

    is_recognized, rec_fuel_type, price = digit_to_price(url)
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
    return f'Ok, recognized fuel_type={rec_fuel_type}, price={price}'
