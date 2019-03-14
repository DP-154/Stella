import random
from datetime import timedelta, datetime, date
from itertools import chain
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database_manupulation import drop_all_tables, create_all, truncate_all_tables
from database.models import (User, FuelCompany, Fuel, GasStation, Images, Price)
from database.queries import get_or_create

TEST_CONNECT = environ['DATABASE_TEST_URL']

engine = create_engine(TEST_CONNECT)
SessionMaker = sessionmaker(bind=engine)


def start_test_db():
    session = SessionMaker()

    users = [get_or_create(session, User, tg_id=52)]
    company_names = ['okko', 'wog']
    companies = [get_or_create(session, FuelCompany, fuel_company_name=n)
                 for n in company_names]

    fuel_marks = ['92', '95']
    fuels = [get_or_create(session, Fuel, fuel_type=f, is_premium=False)
             for f in fuel_marks]

    addresses = ['address1', 'address2', 'address3', 'address4']
    gas_stations = []
    i = 0
    for company in companies:
        for _ in range(len(addresses) // len(companies)):
            gas_stations.append(get_or_create(session, GasStation, address=addresses[i],
                                              fuel_company_id=company.id))
            i += 1

    images = [get_or_create(session, Images, link='link'.join(str(i)), is_recognized=True, is_from_metadata=False)
              for i in range(10)]

    prices = []
    start_date = datetime(date.today().year, date.today().month, date.today().day, 10, 40)

    start_prices = [28, 30]
    for fuel in range(len(fuels)):
        for j in range(len(gas_stations)):
            start_price = start_prices[fuel] + (j % 3) * 0.5
            for i in range(5):
                prices.append(get_or_create(session, Price, price=start_price + 0.2 * i,
                                            date_of_price=start_date - timedelta(hours=12 * i, minutes=j + i),
                                            gas_station_id=gas_stations[j].id,
                                            fuel_id=fuels[fuel].id,
                                            images_id=random.choice(images).id))

    for entity in chain(users, companies, fuels, gas_stations, images, prices):
        session.add(entity)

    session.commit()
    session.close()


def truncate_test_all_tables():
    session = SessionMaker()
    for table in (User, FuelCompany, Fuel, GasStation, Images, Price):
        session.execute(table.__table__.delete())
    session.commit()
    session.close()


def create_test_info():
    truncate_test_all_tables()
    start_test_db()


if __name__== "__main__":
    create_test_info()
