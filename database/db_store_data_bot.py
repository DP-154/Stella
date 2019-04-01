from collections import namedtuple

from database.models import User, FuelCompany, GasStation, Images, Fuel
from database.queries import get_or_create, get_or_none


bot_store = namedtuple('bot_store',
                       ['user', 'company', 'gas_station', 'image'])

def db_store_start(session, tg_id, image_link, company_name, address) -> dict:
    user = get_or_create(session, User, tg_id=tg_id)
    company = get_or_create(session, FuelCompany, fuel_company_name=company_name)

    gas_station = get_or_create(session, GasStation,
                                fuel_company_id=company.id, address=address)
    image = get_or_create(session, Images,
                          link=image_link, is_recognized=False,
                          user_id=user.id)
    store_result = bot_store(user=user,
                             company=company,
                             gas_station=gas_station,
                             image=image)
    return store_result
