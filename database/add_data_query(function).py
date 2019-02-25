from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import models, db_connection

engine = create_engine(db_connection.connect_db())

Session = sessionmaker(bind=engine)
session = Session()

data = {'user': None,
        'gps_location': None,
        'gas_station': None,
        'image_link': None,
        'fuel_company': None,
        'date_of_price': None,
        'price': None,
        'fuel': None,
        'fuel_type': None,
        'is_recognised': None,
        'created_at': None,
        'is_from_metadata': None,
        'created_by': None}


def write_to_db(data_dict):

    price = models.Price(data_dict['price'],
                         data_dict['date_of_price'],
                         data_dict['gas_station'],
                         data_dict['fuel'],
                         data_dict['images'])

    image = models.Images(data_dict['image_link'],
                          data_dict['is_recognised'],
                          data_dict['created_at'],
                          data_dict['is_from_metadata'],
                          data_dict['created_by'],
                          data_dict['user'])

    gas_station = models.GasStation(data_dict['gas_station'],
                                    data_dict['gps_location'],
                                    data_dict['fuel_company'])

    fuel = models.Fuel(data_dict['fuel_type'],
                       data_dict['is_premium'])

    fuel_company = models.FuelCompany(data_dict['fuel_company'])

    session.add(image)
    session.add(fuel_company)
    session.add(gas_station)
    session.add(fuel)
    session.add(price)

    session.commit()


session.close()
