from .models import (Base, User, FuelCompany, Fuel, GasStation,
                    Images, Price)
from .db_connection import engine
from .queries import session_scope

mapping = {
    'user': User,
    'fuelcompany': FuelCompany,
    'fuel_company': FuelCompany,
    'fuel': Fuel,
    'gasstation': GasStation,
    'gas_station': GasStation,
    'images': Images,
    'price': Price
}


def create_all():
    Base.metadata.create_all(engine)


def truncate_tables(*table_names):
    with session_scope() as session:
        tables = [t.lower() for t in table_names]
        for t in tables:
            to_delete = mapping.get(t)
            if to_delete:
                session.execute(to_delete.__table__.delete())


def truncate_all_tables():
    with session_scope() as session:
        for table in (User, FuelCompany, Fuel, GasStation, Images, Price):
            session.execute(table.__table__.delete())


def drop_tables(*table_names):
    tables = [v.__table__ for v in filter(bool, map(mapping.get, table_names))]
    Base.metadata.drop_all(bind=engine, tables=tables)


def drop_all_tables():
    Base.metadata.drop_all(engine)
