import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column('user_name', String)
    date_of_registration = Column('date_of_registration', DateTime, default=datetime.datetime.utcnow())


class FuelCompany(Base):
    __tablename__ = 'fuel_company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fuel_company_name = Column('fuel_company_name', String)


class Fuel(Base):
    __tablename__ = 'fuel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    fuel_connections = relationship("Association")


class GasStation(Base):
    __tablename__ = 'gas_station'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gas_station_name = Column('gas_station_name', String)
    gps_location = Column('gps_location', String)
    fuel_company_id = Column(Integer, ForeignKey('fuel_company.id'))
    fuel_company = relationship("FuelCompany")
    gas_station_connections = relationship("Association")


class Images(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dropbox_link = Column('dropbox_link', String)
    is_recognized = Column('is_recognized', Boolean)
    date_of_download = Column('date_of_download', DateTime, default=datetime.datetime.utcnow())
    images_connections = relationship("Association")


class PriceAndDate(Base):
    __tablename__ = 'price_and_date'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column('price', String, nullable=False)
    date_of_price = Column('date_of_price', DateTime, default=datetime.datetime.utcnow())
    price_and_date_connections = relationship("Association")


class Association(Base):
    __tablename__ = 'association'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column('price', String)
    price_and_date_id = Column(Integer, ForeignKey('price_and_date.id'), primary_key=True)
    images_id = Column(Integer, ForeignKey('images.id'), primary_key=True)
    gas_station_id = Column(Integer, ForeignKey('gas_station.id'), primary_key=True)
    fuel_id = Column(Integer, ForeignKey('fuel.id'), primary_key=True)

    price_and_date = relationship("PriceAndDate", back_populates="")
    images = relationship("Images", back_populates="")
    gas_station = relationship("GasStation", back_populates="")
    fuel = relationship("Fuel", back_populates="")

