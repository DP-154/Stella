from .models import (Base, User, FuelCompany, Fuel, GasStation,
                    Images, Price)
from .db_connection import session_maker, engine

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
    session = session_maker()
    tables = [t.lower() for t in table_names]
    for t in tables:
        to_delete = mapping.get(t)
        if to_delete:
            session.execute(to_delete.__table__.delete())
    session.commit()


def truncate_all_tables():
    session = session_maker()
    for table in (User, FuelCompany, Fuel, GasStation, Images, Price):
        session.execute(table.__table__.delete())
    session.commit()


def drop_tables(*table_names):
    tables = [v.__table__ for v in filter(bool, map(mapping.get, table_names))]
    Base.metadata.drop_all(bind=engine, tables=tables)


def drop_all_tables():
    Base.metadata.drop_all(engine)
