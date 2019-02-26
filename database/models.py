import datetime
<<<<<<< HEAD
import uuid

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
=======
from sqlalchemy import (Column, String, DateTime, Integer,
                        Boolean, ForeignKey, DECIMAL)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
    user_name = Column('user_name', String)
    date_of_registration = Column('date_of_registration', DateTime, default=datetime.datetime.utcnow())
    images_connections = relationship('Images')

=======
    id = Column(UUID(as_uuid=True), primary_key=True)
    tg_id = Column('tg_id', Integer)
    date_of_registration = Column('date_of_registration', DateTime, default=datetime.datetime.utcnow())
    images_connections = relationship('Images')

    def __init__(self, tg_id, date_of_registration=datetime.datetime.utcnow()):
        self.tg_id = tg_id
        self.date_of_registration = date_of_registration

>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837

class FuelCompany(Base):
    __tablename__ = 'fuel_company'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
    fuel_company_name = Column('fuel_company_name', String)
    gas_station_connection = relationship('GasStation')

=======
    id = Column(UUID(as_uuid=True), primary_key=True)
    fuel_company_name = Column('fuel_company_name', String)
    gas_station_connection = relationship('GasStation')

    def __init__(self, fuel_company_name):
        self.fuel_company_name = fuel_company_name
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837


class Fuel(Base):
    __tablename__ = 'fuel'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    price_connections = relationship('Price')
=======
    id = Column(UUID(as_uuid=True), primary_key=True)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    price_connections = relationship('Price', backref='fuel')

    def __init__(self, fuel_type, is_premium):
        self.fuel_type = fuel_type
        self.is_premium = is_premium

    def __init__(self, fuel_type, is_premium):
        self.fuel_type = fuel_type
        self.is_premium = is_premium

    def __init__(self, fuel_type, is_premium):
        self.fuel_type = fuel_type
        self.is_premium = is_premium
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837


class GasStation(Base):
    __tablename__ = 'gas_station'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
    gas_station_name = Column('gas_station_name', String)
    gps_location = Column('gps_location', String)
    fuel_company_id = Column(Integer, ForeignKey('fuel_company.id'))
    fuel_company_connection = relationship('FuelCompany')
    price_connections = relationship('Price')
=======
    id = Column(UUID(as_uuid=True), primary_key=True)
    address = Column('address', String)
    fuel_company_id = Column(Integer, ForeignKey('fuel_company.id',
                                                 ondelete='CASCADE'))
    fuel_company_connection = relationship('FuelCompany')
    price_connections = relationship('Price', backref='gas_station')
    
    def __init__(self, address, fuel_company_id):
        self.address = address
        self.fuel_company_id = fuel_company_id

    def __init__(self, gas_station_name, gps_location, fuel_company):
        self.gas_station_name = gas_station_name
        self.gps_location = gps_location
        self.fuel_company_id = fuel_company

    def __init__(self, gas_station_name, gps_location, fuel_company):
        self.gas_station_name = gas_station_name
        self.gps_location = gps_location
        self.fuel_company_id = fuel_company
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837


class Images(Base):
    __tablename__ = 'images'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
=======
    id = Column(UUID(as_uuid=True), primary_key=True)
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837
    link = Column('link', String)
    is_recognized = Column('is_recognized', Boolean)
    created_at = Column('created_at', DateTime, default=datetime.datetime.utcnow())
    is_from_metadata = Column('is_from_metadata', Boolean)
<<<<<<< HEAD
    created_by = Column('created_by', String)
    user_id = Column(uuid, ForeignKey('user.id'))
    user_connections = relationship('User')
    price_connections = relationship('Price')
=======
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user_connections = relationship('User')
    price_connections = relationship('Price', backref='image')

    def __init__(self, link, is_recognized, user_id, is_from_metadata=False, created_at=datetime.datetime.utcnow()):
        self.link = link
        self.is_recognized = is_recognized
        self.created_at = created_at
        self.is_from_metadata = is_from_metadata
        self.user_id = user_id

    def __init__(self, link, is_recognized, created_at, is_from_metadata, created_by, user):
        self.link = link
        self.is_recognized = is_recognized
        self.created_at = created_at
        self.is_from_metadata = is_from_metadata
        self.created_by = created_by
        self.user_id = user

    def __init__(self, link, is_recognized, created_at, is_from_metadata, created_by, user):
        self.link = link
        self.is_recognized = is_recognized
        self.created_at = created_at
        self.is_from_metadata = is_from_metadata
        self.created_by = created_by
        self.user_id = user
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837


class Price(Base):
    __tablename__ = 'price'

<<<<<<< HEAD
    id = Column(uuid, primary_key=True)
    price = Column('price', DECIMAL(precision=2), nullable=False)
    date_of_price = Column('date_of_price', DateTime, default=datetime.datetime.utcnow())
    gas_station_id = Column(uuid, ForeignKey('gas_station.id'))
    fuel_id = Column(uuid, ForeignKey('fuel.id'))
    images_id = Column(uuid, ForeignKey('images.id'))

=======
    id = Column(UUID(as_uuid=True), primary_key=True)
    price = Column('price', DECIMAL(7, 2), nullable=False)
    date_of_price = Column('date_of_price', DateTime, default=datetime.datetime.utcnow())
    gas_station_id = Column(Integer, ForeignKey('gas_station.id',
                                                ondelete='CASCADE'))
    fuel_id = Column(Integer, ForeignKey('fuel.id', ondelete='CASCADE'))
    images_id = Column(Integer, ForeignKey('images.id', ondelete='CASCADE'))
    
    def __init__(self, price, gas_station, fuel, image, date_of_price=datetime.datetime.utcnow()):
        self.price = price
        self.date_of_price = date_of_price
        self.gas_station_id = gas_station
        self.fuel_id = fuel
        self.images_id = image
>>>>>>> a75ad5ffbbd826e99d2e4a26e204335d91a52837
