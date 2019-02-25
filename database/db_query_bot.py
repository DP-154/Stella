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

def day_to_num(day) -> int:
    digits = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
              "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
              "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
              "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,}
    if isinstance(day, date):
        return day
    elif isinstance(day, int):
        delta = find_timedelta(day)
        return delta
    elif isinstance(day, str):
        if day == "week":
            num_date = 7
        elif day == "month":
            num_date = 30
        else:
            word_list = day.split()
            num_date = 0
            for digit in word_list:
                for k, v in digits.items():
                    if k == digit: num_date += v
        delta = find_timedelta(num_date)
    return delta

def find_timedelta(days) -> date:
    new_delta = timedelta(days=days)
    time_period = date.today() - new_delta
    return time_period

def get_date_subquery(days, session) -> subquery:
    if days is not None:
        days = day_to_num(days)
        subquery = session.query(Price.date_of_price).filter(Price.date_of_price == days
                                                                 ).distinct(Price.date_of_price).subquery()
    else:
        subquery = session.query(func.max(Price.date_of_price).label("date_of_price")).subquery()
    return subquery

def min_price_subquery(day, session) -> subquery:
    subquery_date = get_date_subquery(day, session)
    subquery = session.query(Price.price, Price.date_of_price,Price.fuel_id,
                             func.rank().over(partition_by=Price.fuel_id, order_by=Price.price
                             ).label("price_rank")
                             ).filter(Price.date_of_price == subquery_date.c.date_of_price).subquery()
    return subquery

def query_by_station_current_date(company_name, gas_station, days=None) -> str:
    new_session = Session()
    subquery = get_date_subquery(days, new_session)

    result = new_session.query(Price.price, GasStation.gas_station_name, Price.date_of_price, Fuel.fuel_type, subquery
                               ).join(Fuel).join(GasStation
                               ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                               ).filter(FuelCompany.fuel_company_name == company_name
                               ).filter(GasStation.gas_station_name == gas_station
                               ).filter(Price.date_of_price == subquery.c.date_of_price).all()

    pricelist = "Prices at {}, {}:\n".format(company_name, gas_station)
    for row in result:
        pricelist = pricelist + "{}: {} as of {}\n".format(row.fuel_type, row.price, row.date_of_price)
    new_session.close()
    return pricelist


def query_avg_all_stations(days=None) -> str:
    new_session = Session()
    subquery = get_date_subquery(days, new_session)

    result = new_session.query(func.avg(Price.price).label("average_price"),
                               Fuel.fuel_type, subquery, Price.date_of_price
                               ).join(Fuel
                               ).filter(subquery.c.date_of_price == Price.date_of_price
                               ).group_by(Fuel.fuel_type, subquery, Price.date_of_price
                               ).order_by(Fuel.fuel_type).all()

    pricelist = "Recent gas prices (shown by average):\n"
    for row in result:
        pricelist = pricelist + "{}: {} as of {}\n".format(row.fuel_type, round(row.average_price, 2), row.date_of_price)
    new_session.close()
    return pricelist


def query_by_station_min_price(fuel_name, days=None) -> str:
    new_session = Session()
    subquery_price = min_price_subquery(days, new_session)
    subquery_date = get_date_subquery(days, new_session)
    result = new_session.query(Price.price, Price.date_of_price, Fuel.fuel_type, GasStation.gas_station_name,
                               FuelCompany.fuel_company_name
                               ).filter(subquery_price.c.price_rank == 1
                               ).join(Fuel).join(GasStation
                               ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                               ).filter(Fuel.fuel_type == fuel_name
                               ).filter(Price.date_of_price == subquery_date.c.date_of_price
                               ).order_by(Price.price).limit(1).all()

    pricelist = "Gas station with the lowest price of {} fuel:\n".format(fuel_name)
    for row in result:
        pricelist = pricelist + "{}, {}: {} - {} ({})\n".format(row.fuel_company_name, row.gas_station_name,
                                                               row.fuel_type, row.price, row.date_of_price)
    new_session.close()
    return pricelist
