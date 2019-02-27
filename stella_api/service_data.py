from collections import namedtuple

from database.db_connection import session_maker
from database.db_store_data_bot import db_store_start, db_get_fuel, db_store_recognized
from stella_api.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from stella_api.image_recognition import digit_to_price

TMP_IS_PREMIUM = False
TMP_IS_RECOGNIZED = True
TMP_IS_FROM_METADATA = False


def store_bot_data(tg_id, image_link, latitude, longitude):
    md_from_coordinates = MetaDataFromCoordinates(latitude, longitude)
    company_name = md_from_coordinates.get_name()
    address = md_from_coordinates.get_address()

    session = session_maker()
    stored_data = db_store_start(session, tg_id, image_link, company_name, address)

    recognized_info = digit_to_price(image_link).split(',')
    is_recognized=recognized_info[0]
    if is_recognized:
        rec_fuel_type = recognized_info[1]
        is_premium = TMP_IS_PREMIUM
        fuel = db_get_fuel(session, rec_fuel_type, is_premium)
        if fuel is None:
            return "There isn't a fuel {} in database".format(rec_fuel_type)

        if recognized_info[2].replace('.', '', 1).isdigit():
            rec_price = float(recognized_info[2])
            recognition_result = namedtuple('rec_result', ['is_recognized', 'fuel_type', 'price'])
            rr = recognition_result(is_recognized, rec_fuel_type, rec_price)

            location_result = namedtuple('loc_result', ['gas_station', 'is_from_metadata'])
            lr = location_result(stored_data['gas_station'].id, TMP_IS_FROM_METADATA)
            db_store_recognized(session, stored_data['image'], rr, lr)
        else:
            return "{} is not a float number".format(recognized_info[2])
    else:
        return 'photo is not recognized'
    session.close()
    return 'Ok'
