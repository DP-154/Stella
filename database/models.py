import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(uuid, primary_key=True)
    user_name = Column('user_name', String)
    date_of_registration = Column('date_of_registration', DateTime, default=datetime.datetime.utcnow())


class FuelCompany(Base):
    __tablename__ = 'fuel_company'

    id = Column(uuid, primary_key=True)
    fuel_company_name = Column('fuel_company_name', String)


class Fuel(Base):
    __tablename__ = 'fuel'

    id = Column(uuid, primary_key=True)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    fuel_connections = relationship("Association")


class GasStation(Base):
    __tablename__ = 'gas_station'

    id = Column(uuid, primary_key=True)
    gas_station_name = Column('gas_station_name', String)
    gps_location = Column('gps_location', String) # поиска gps тип данных
    fuel_company_id = Column(Integer, ForeignKey('fuel_company.id'))
    fuel_company = relationship("FuelCompany")
    gas_station_connections = relationship("Association")


class Images(Base):
    __tablename__ = 'images'

    id = Column(uuid, primary_key=True)
    link = Column('link', String)
    is_recognized = Column('is_recognized', Boolean)
    created_at = Column('created_at', DateTime, default=datetime.datetime.utcnow())
    created_by = Column('creted_by', String)
    images_connections = relationship("Association")


class Price(Base):
    __tablename__ = 'price'

    id = Column(uuid, primary_key=True)
    price = Column('price', DECIMAL(precision=2), nullable=False)
    date_of_price = Column('date_of_price', DateTime, default=datetime.datetime.utcnow())
    price_and_date_connections = relationship("Association")


class Association(Base):
    __tablename__ = 'association'

    id = Column(uuid, primary_key=True)
    price_id = Column(uuid, ForeignKey('price.id'))
    images_id = Column(uuid, ForeignKey('images.id'))
    gas_station_id = Column(uuid, ForeignKey('gas_station.id'))
    fuel_id = Column(uuid, ForeignKey('fuel.id'))

    price = relationship("Price", back_populates="")
    images = relationship("Images", back_populates="")
    gas_station = relationship("GasStation", back_populates="Fuel")
    fuel = relationship("Fuel", back_populates="GasStation")

