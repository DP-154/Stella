import datetime
from sqlalchemy import (Column, String, DateTime, Integer,
                        Boolean, ForeignKey, DECIMAL)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column('username', String)
    password_hash = Column('password_hash', String)
    tg_id = Column('tg_id', Integer)
    date_of_registration = Column('date_of_registration', DateTime, default=datetime.datetime.utcnow())
    images_connections = relationship('Images')

    def __init__(self, tg_id, date_of_registration=datetime.datetime.utcnow()):
        self.tg_id = tg_id
        self.date_of_registration = date_of_registration

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FuelCompany(Base):
    __tablename__ = 'fuel_company'

    id = Column(UUID(as_uuid=True), primary_key=True)
    fuel_company_name = Column('fuel_company_name', String)
    gas_station_connection = relationship('GasStation')

    def __init__(self, fuel_company_name):
        self.fuel_company_name = fuel_company_name


class Fuel(Base):
    __tablename__ = 'fuel'

    id = Column(UUID(as_uuid=True), primary_key=True)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    price_connections = relationship('Price', backref='fuel')

    def __init__(self, fuel_type, is_premium):
        self.fuel_type = fuel_type
        self.is_premium = is_premium


class GasStation(Base):
    __tablename__ = 'gas_station'

    id = Column(UUID(as_uuid=True), primary_key=True)
    address = Column('address', String)
    fuel_company_id = Column(Integer, ForeignKey('fuel_company.id',
                                                 ondelete='CASCADE'))
    fuel_company_connection = relationship('FuelCompany')
    price_connections = relationship('Price', backref='gas_station')

    def __init__(self, address, fuel_company_id):
        self.address = address
        self.fuel_company_id = fuel_company_id


class Images(Base):
    __tablename__ = 'images'

    id = Column(UUID(as_uuid=True), primary_key=True)
    link = Column('link', String)
    is_recognized = Column('is_recognized', Boolean)
    created_at = Column('created_at', DateTime, default=datetime.datetime.utcnow())
    is_from_metadata = Column('is_from_metadata', Boolean)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user_connections = relationship('User')
    price_connections = relationship('Price', backref='image')

    def __init__(self, link, is_recognized, user_id, is_from_metadata=False, created_at=datetime.datetime.utcnow()):
        self.link = link
        self.is_recognized = is_recognized
        self.created_at = created_at
        self.is_from_metadata = is_from_metadata
        self.user_id = user_id


class Price(Base):
    __tablename__ = 'price'

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
