from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import DatabaseConfig
from database.models import FuelCompany, GasStation, Fuel, Price

db_conf = DatabaseConfig()
engine = create_engine('postgresql://{}:{}@{}/{}'.format(db_conf.db_user, db_conf.db_password, db_conf.db_host,
                                                                  db_conf.db_name))
Session = sessionmaker(bind=engine)

def date_to_num(date) -> int:
    digits = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
              "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
              "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
              "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,}
    if isinstance(date, int):
        num_date = date
    elif isinstance(date, str):
        if date == "week":
            num_date = 7
        elif date == "month":
            num_date = 30
        else:
            word_list = date.split()
            num_date = 0
            for digit in word_list:
                for k, v in digits.items():
                    if k == digit: num_date += v
    return num_date

def find_timedelta(days) -> date:
    num_days = date_to_num(days)
    new_delta = timedelta(days=num_days)
    time_period = date.today() - new_delta
    return time_period

def query_by_gas_station(company_name, gas_station, date_of_price=date.today()) -> str:
    new_session = Session()
    result = new_session.query(Price.price, Fuel.fuel_type, GasStation.gas_station_name).join(GasStation).join(Fuel
                                             ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                                             ).filter(FuelCompany.fuel_company_name == company_name
                                             ).filter(GasStation.gas_station_name == gas_station
                                             ).filter(Price.date_of_price == date_of_price
                                             ).order_by(Fuel.fuel_type).all()

    pricelist = "Prices at {}, {} as of {}:\n".format(company_name, gas_station, date_of_price)
    for row in result:
        pricelist = pricelist + "{}: {}\n".format(row.fuel_type, row.price)
    new_session.close()
    return pricelist

def query_avg_all_stations(days=1) -> str:
    new_session = Session()

    time_period = find_timedelta(date_to_num(days))

    result = new_session.query(func.avg(Price).label("average_price"), Fuel.fuel_type
                               ).join(Fuel).group_by(Fuel.fuel_type, Price.date_of_price
                               ).having(Price.date_of_price > time_period).order_by(Fuel.fuel_type).all()

    pricelist = "Gas prices for last {} days:\n".format(days)
    for row in result:
        pricelist = pricelist + "{}: {}\n".format(row.fuel_type, row.average_price)
    new_session.close()
    return pricelist

def query_avg_by_station(company_name, gas_station, days=1) -> str:
    new_session = Session()

    time_period = find_timedelta(date_to_num(days))

    result = new_session.query(func.avg(Price.price).label("average_price"), Fuel.fuel_type, GasStation.gas_station_name
                               ).join(Fuel).join(GasStation).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                               ).filter(FuelCompany.fuel_company_name == company_name
                               ).filter(GasStation.gas_station_name == gas_station
                               ).filter(Price.date_of_price > time_period
                               ).group_by(Fuel.fuel_type, GasStation.gas_station_name).order_by(Fuel.fuel_type).all()

    pricelist = "Prices at {}, {} for last {} days:\n".format(company_name, gas_station, days)
    for row in result:
        pricelist = pricelist + "{}: {}".format(row.fuel_type, row.average_price)
    new_session.close()
    return pricelist
