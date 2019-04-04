from operator import attrgetter
from contextlib import contextmanager
from datetime import datetime, date, timedelta

from sqlalchemy.sql import func

from .db_connection import session_maker
from .models import (FuelCompany, GasStation, User, Images, Fuel,
                     Price)


@contextmanager
def session_scope():
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


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


def list_fuels(session):
    instances = session.query(Fuel).all()
    return list(map(attrgetter('fuel_type'), instances))


def custom_query(session, **kwargs):
    date_ = kwargs.get('date')
    companies_list = kwargs.get('companies_list')
    gas_station_list = kwargs.get('gas_station_list')
    fuel_types_list = kwargs.get('fuel_types_list')
    aggregate = kwargs.get('aggregate')

    if aggregate and aggregate in ('min', 'max', 'avg'):
        mapping = {'min': func.min, 'max': func.max, 'avg': func.avg}
        q = session.query(mapping[aggregate](Price.price).label('average'))
    else:
        q = session.query(Price)

    if date_:
        if isinstance(date_, tuple) or isinstance(date_, list):
            from_, to = date_
            if isinstance(from_, datetime):
                from_ = from_.strftime('%Y-%m-%d')
            if isinstance(to, datetime):
                to = to.strftime('%Y-%m-%d')
            q = q.filter(Price.date_of_price.between(from_, to))
        elif isinstance(date_, datetime):
            #now = date(*[int(i) for i in date_.split('-')])
            next_ = (date_ + timedelta(days=1)).strftime('%Y-%m-%d')
            prev = (date_ - timedelta(days=1)).strftime('%Y-%m-%d')
            q = q.filter(Price.date_of_price.between(prev, next_))

    if companies_list:
        q = (q
             .join(GasStation, FuelCompany)
             .filter(FuelCompany.fuel_company_name.in_(companies_list)))
    elif gas_station_list:
        q = (q
             .join(GasStation)
             .filter(GasStation.address.in_(gas_station_list)))
    if fuel_types_list:
        q = (q
             .join(Fuel)
             .filter(Fuel.fuel_type.in_(fuel_types_list)))
    return q.all()


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
                       is_premium=False)
    if not fuel:
        get_or_create(session, Fuel, fuel_type=recognition_result.fuel_type, is_premium=False)
    price = Price(price=recognition_result.price,
                  gas_station=location_result.gas_station,
                  fuel=fuel,
                  image=image)
    session.add(image)
    session.add(price)
    session.commit()
