import datetime
from uuid import uuid1

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    username = Column('username', String)
    password_hash = Column('password_hash', String)
    tg_id = Column('tg_id', Integer)
    date_of_registration = Column('date_of_registration', DateTime,
                                  default=datetime.datetime.utcnow)
    images_connections = relationship('Images')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FuelCompany(Base):
    __tablename__ = 'fuel_company'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    fuel_company_name = Column('fuel_company_name', String)
    gas_station_connection = relationship('GasStation', backref='fuel_company')


class Fuel(Base):
    __tablename__ = 'fuel'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    fuel_type = Column('fuel_type', String, nullable=False)
    is_premium = Column('is_premium', Boolean)
    price_connections = relationship('Price', backref='fuel')


class GasStation(Base):
    __tablename__ = 'gas_station'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    address = Column('address', String)
    fuel_company_id = Column(UUID(as_uuid=True),
                             ForeignKey('fuel_company.id', ondelete='CASCADE'))
    fuel_company_connection = relationship('FuelCompany')
    price_connections = relationship('Price', backref='gas_station')


class Images(Base):
    __tablename__ = 'images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    link = Column('link', String)
    is_recognized = Column('is_recognized', Boolean)
    created_at = Column('created_at', DateTime,
                        default=datetime.datetime.utcnow)
    is_from_metadata = Column('is_from_metadata', Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user_connections = relationship('User')
    price_connections = relationship('Price', backref='image')


class Price(Base):
    __tablename__ = 'price'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    price = Column('price', DECIMAL(7, 2), nullable=False)
    date_of_price = Column('date_of_price', DateTime,
                           default=datetime.datetime.utcnow)
    gas_station_id = Column(UUID(as_uuid=True), ForeignKey('gas_station.id',
                                                           ondelete='CASCADE'))
    fuel_id = Column(UUID(as_uuid=True), ForeignKey('fuel.id',
                                                    ondelete='CASCADE'))
    images_id = Column(UUID(as_uuid=True), ForeignKey('images.id',
                                                      ondelete='CASCADE'))
