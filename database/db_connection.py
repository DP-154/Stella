import os

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as SessionMaker

from config import DatabaseConfig

engine = create_engine(os.environ['DATABASE_URL'], echo=True)

session_maker = SessionMaker(bind=engine)


def connect_db():
    db_conf = DatabaseConfig()
    return psycopg2.connect(host=db_conf.db_host,
                            database=db_conf.db_name,
                            user=db_conf.db_user,
                            password=db_conf.db_password)
