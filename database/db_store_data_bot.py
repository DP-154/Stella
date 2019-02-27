from database.models import User, FuelCompany, GasStation, Images, Fuel
from database.queries import get_or_create, get_or_none, update_image


def db_store_start(session, tg_id, image_link, company_name, address) -> dict:
    user = get_or_create(session, User, tg_id=tg_id)
    company = get_or_create(session, FuelCompany, fuel_company_name=company_name)

    store_result = {
        'user': user,
        'company': company,
        'gas_station': get_or_create(session, GasStation, fuel_company_id=company.id, address=address),
        'image': get_or_create(session, Images, link=image_link, is_recognized=False, user_id=user.id)
    }
    return store_result


def db_get_fuel(session, fuel_type, is_premium) -> Fuel:
    return get_or_none(session, Fuel, fuel_type=fuel_type, is_premium=is_premium)


def db_store_recognized(session, image, recognition_result, location_result):
    update_image(session, image, recognition_result, location_result)
