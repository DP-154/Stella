from collections import namedtuple

import database.queries as q
from stella_api.imageMetadata.coordinates_metadata import MetaDataFromCoordinates

from database.db_connection import session_maker
from database.models import User, FuelCompany, GasStation, Fuel, Images
from stella_api.image_recognition import digit_to_price


def store_bot_data(tg_id, image_link, new_location):
    md_from_coordinates = MetaDataFromCoordinates(new_location.latitude, new_location.longitude)

    company_name = md_from_coordinates.get_name()

    address = md_from_coordinates.get_address()
    try:

        session = session_maker()

        user = q.get_or_create(session, User, tg_id=tg_id)

        company = q.get_or_create(session, FuelCompany, fuel_company_name=company_name)

        gas_station = q.get_or_create(session, GasStation, fuel_company_id=company.id, address=address)

        image = q.get_or_create(session, Images, link=image_link,
                                is_recognized=False,
                                user_id=user.id)

        recognized_price_list = digit_to_price(image_link).split(',')
        rec_fuel_type = recognized_price_list[0]
        try:
            rec_price = float(recognized_price_list[1])
        except:
            rec_price = None
        is_premium = False

        fuel = q.get_or_none(session, Fuel, fuel_type=rec_fuel_type, is_premium=is_premium)
        if fuel is None:
            return "There isn't a {} in database".format(rec_fuel_type)

        if rec_price is not None:
            recognition_result = namedtuple('rec_result', ['is_recognized', 'fuel_type', 'price'])
            rr = recognition_result(True, rec_fuel_type, rec_price)

            location_result = namedtuple('loc_result', ['gas_station', 'is_from_metadata'])
            lr = location_result(gas_station.id, False)
            q.update_image(session, image, rr, lr)
        else:
            return "price {} is not recognized".format(recognized_price_list[1])
    except:
        return "something wrong while storing"
    return "Everything ok. Thank you"
