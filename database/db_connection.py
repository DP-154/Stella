import os

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as SessionMaker

from config import DatabaseConfig
DATABASE_URL='postgres://kqpmfuegypaqeo:cf9cf9db21b192df1253509893b29369891a97c4165c40cdbb038565c0a58ce1@ec2-79-125-6-250.eu-west-1.compute.amazonaws.com:5432/de8na53ov1p0au'
engine = create_engine(DATABASE_URL, echo=True)
session_maker = SessionMaker(bind=engine)

def connect_db():
    db_conf = DatabaseConfig()
    return psycopg2.connect(host=db_conf.db_host,
                            database=db_conf.db_name,
                            user=db_conf.db_user,
                            password=db_conf.db_password)


def made_sql(db_con, sql) -> bool:
    try:
        with db_con:
            with db_con.cursor() as curs:
                curs.execute(sql)
                return True
    except psycopg2.Error:
        return False


def create_schema(db_con, sch_name):
    return made_sql(db_con, 'CREATE SCHEMA {};'.format(sch_name))


def drop_schema(db_con, sch_name):
    return made_sql(db_con, 'DROP SCHEMA {} CASCADE;'.format(sch_name))


def create_table(db_con, table_structure):
    return made_sql(db_con, 'CREATE TABLE {};'.format(table_structure))


def drop_table(db_con, table_name):
    return made_sql(db_con, 'DROP TABLE {};'.format(table_name))
