from sqlalchemy.sql import func
from database.db_connection import session_maker
from database.models import FuelCompany, GasStation, Fuel, Price
Session = session_maker()


def get_date_subquery(day, session):
    if day is not None:
        subquery = session.query(Price.date_of_price).filter(Price.date_of_price == day
                                                             ).distinct(Price.date_of_price).subquery()
    else:
        subquery = session.query(func.max(Price.date_of_price).label("date_of_price")).subquery()
    return subquery


def min_price_subquery(day, session):
    subquery_date = get_date_subquery(day, session)
    subquery = session.query(Price.price, Price.date_of_price,Price.fuel_id,
                             func.rank().over(partition_by=Price.fuel_id, order_by=Price.price
                             ).label("price_rank")
                             ).filter(Price.date_of_price == subquery_date.c.date_of_price).subquery()
    return subquery


def query_by_station_current_date(company_name, gas_station, day=None) -> str:
    new_session = Session()
    subquery = get_date_subquery(day, new_session)

    result = new_session.query(Price.price, GasStation.address, Price.date_of_price, Fuel.fuel_type, subquery
                               ).join(Fuel).join(GasStation
                               ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                               ).filter(FuelCompany.fuel_company_name == company_name
                               ).filter(GasStation.address == gas_station
                               ).filter(Price.date_of_price == subquery.c.date_of_price)

    new_session.close()
    return result


def query_avg_all_stations(days=None) -> str:
    new_session = Session()
    subquery = get_date_subquery(days, new_session)

    result = new_session.query(func.avg(Price.price).label("average_price"),
                               Fuel.fuel_type, subquery, Price.date_of_price
                               ).join(Fuel
                               ).filter(subquery.c.date_of_price == Price.date_of_price
                               ).group_by(Fuel.fuel_type, subquery, Price.date_of_price
                               ).order_by(Fuel.fuel_type)

    new_session.close()
    return result


def query_by_station_min_price(fuel_name, days=None) -> str:
    new_session = Session()
    subquery_price = min_price_subquery(days, new_session)
    subquery_date = get_date_subquery(days, new_session)
    result = new_session.query(Price.price, Price.date_of_price, Fuel.fuel_type, GasStation.address,
                               FuelCompany.fuel_company_name
                               ).filter(subquery_price.c.price_rank == 1
                               ).join(Fuel).join(GasStation
                               ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                               ).filter(Fuel.fuel_type == fuel_name
                               ).filter(Price.date_of_price == subquery_date.c.date_of_price
                               ).order_by(Price.price).limit(1)

    new_session.close()
    return result


if __name__ == '__main__':
    result = query_by_station_min_price('А97', '2019-02-24')
