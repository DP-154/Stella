from operator import attrgetter

from .models import (FuelCompany, GasStation, User, Images, Fuel,
                     Price)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_or_none(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance


def list_fuel_company_names(session):
    instances = session.query(FuelCompany).all()
    return list(map(attrgetter('fuel_company_name'), instances))


"""
following functions meant to be used in following flow:
get image link, location and telegram id -> create base image ->
-> use recognition and location extraction -> update image and create
related entities
"""


def create_base_image(session, tg_id, image_link):
    user = get_or_create(session, User, tg_id=tg_id)
    image = Images(link=image_link,
                   is_recognized=False,
                   user_connections=user)
    session.add(image)
    session.commit()
    return image


def acquire_gas_station(session, company_name, address):
    company = (session.query(FuelCompany)
               .filter(FuelCompany.fuel_company_name == company_name)
               .first())
    return get_or_create(session, GasStation,
                         fuel_company_connection=company,
                         address=address)


def update_image(session, image, recognition_result, location_result):
    """
    recognition_result type is namedtuple(['is_recognized', 'fuel_type', 'price'])
    location_result type is namedtuple(['gas_station', is_from_metadata])

    besides of image update, also creates price instance
    """

    if not recognition_result.is_recognized:
        # don't change image
        return

    image.is_recognized = recognition_result.is_recognized
    image.is_from_metadata = location_result.is_from_metadata

    fuel = get_or_none(session, Fuel,
                       fuel_type=recognition_result.fuel_type,
                       is_premium=False)  # TODO: should be handled by recognition
    if not fuel:
        raise RuntimeError('incorrect fuel type retrieved '
                           'from recognition result')

    price = Price(price=recognition_result.price,
                  gas_station=location_result.gas_station,
                  fuel=fuel,
                  image=image)

    session.add(image)
    session.add(price)
    session.commit()
