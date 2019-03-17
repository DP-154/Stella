from datetime import datetime, date, timedelta
from decimal import Decimal
from os import environ

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db_query_bot import days_to_date, get_period, query_by_station_min_price, \
    query_avg_all_stations, query_by_station_current_date, query_avg_price_period, query_all_price_period
from tests.integration.database_test_query import start_test_db

from database.models import Base

TEST_CONNECT = environ['DATABASE_TEST_URL']

engine = create_engine(TEST_CONNECT)
SessionMaker = sessionmaker(bind=engine)

session = SessionMaker()


@pytest.fixture(scope="module", autouse=True)
def prepare_test_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    start_test_db()
    yield
    session.close()
    Base.metadata.drop_all(engine)


class TestDaysToDate:
    def test_days_to_date_date(self):
        assert days_to_date(date(2019, 3, 4)) == date(2019, 3, 4)

    def test_days_to_date_datetime(self):
        assert days_to_date(datetime(2019, 3, 4, 10, 45)) == date(2019, 3, 4)

    def test_days_to_date_string_positive(self):
        assert days_to_date('2019-03-04') == date(2019, 3, 4)

    def test_days_to_date_string_wrong_format(self):
        assert days_to_date('04.03.2019') is None

    def test_days_to_date_empty(self):
        assert days_to_date(None) is None


class TestGetPeriod:
    def test_get_period_two_dates(self):
        assert get_period(date(2019, 3, 4), date(2019, 3, 6)) == (date(2019, 3, 4), date(2019, 3, 6))

    def test_get_period_one_date(self):
        assert get_period(None, date(2019, 3, 14)) == (date(2019, 3, 4), date(2019, 3, 14))

    def test_get_period_no_date(self):
        assert get_period(None, None)[1] == date.today()


class TestQueryByStationCurrentDate:

    def test_query_by_station_current_date_max_date(self):
        q = query_by_station_current_date(session, 'okko', 'address1')
        max_date = datetime(date.today().year, date.today().month, date.today().day, 10, 40)
        assert q.count() == 2
        assert q[0] == (pytest.approx(28, 0.01), max_date, '92', 'address1')

    def test_query_by_station_current_date_with_date(self):
        cur_date = date.today() - timedelta(days=1)
        q = query_by_station_current_date(session, 'okko', 'address1', date.today() - timedelta(days=1))
        assert q.count() == 4
        assert (abs(q[0][0] - Decimal(28.2))) < 0.01
        assert q[0][1] == datetime(cur_date.year, cur_date.month, cur_date.day, 22, 39)
        assert q[0][2] == '92'

    def test_query_by_station_current_date_no_info(self):
        q = query_by_station_current_date(session, 'okko', 'address1', date.today() + timedelta(days=2))
        assert q.count() == 0


class TestQueryAVGAllStation:
    def test_query_avg_all_stations_max_date(self):
        q = query_avg_all_stations(session)
        assert q.count() == 2
        assert (abs(q[0][0] - Decimal(28.38))) < 0.01
        assert q[0][1] == date.today()
        assert q[0][2] == '92'

    def test_query_avg_all_stations_with_date(self):
        cur_date = date.today() - timedelta(days=1)
        q = query_avg_all_stations(session, cur_date)
        assert q.count() == 2
        assert (abs(q[0][0] - Decimal(28.68))) < 0.01
        assert q[0][1] == cur_date
        assert q[0][2] == '92'

    def test_query_avg_all_stations_no_info(self):
        q = query_avg_all_stations(session, date.today() + timedelta(days=2))
        assert q.count() == 0


class TestQueryByStationMinPrice:
    def test_query_by_station_min_price_max_date(self):
        q = query_by_station_min_price(session, '95')
        max_date = datetime(date.today().year, date.today().month, date.today().day, 10, 40)
        assert q[0] == (30, max_date, '95', 'address1', 'okko')

    def test_query_by_station_min_price_with_date(self):
        cur_date = date.today() - timedelta(days=1)
        q = query_by_station_min_price(session, '95', cur_date)
        assert (abs(q[0][0] - Decimal(30.2))) < 0.01
        assert q[0][1] == datetime(cur_date.year, cur_date.month, cur_date.day, 22, 39)
        assert q[0][2] == '95'
        assert q[0][3] == 'address1'
        assert q[0][4] == 'okko'

    def test_query_by_station_min_price_no_info(self):
        q = query_by_station_min_price(session, '95', date.today() + timedelta(days=2))
        assert q.count() == 0


class TestQueryAVGPricePeriod:
    def test_query_avg_price_period_without_date(self):
        q = query_avg_price_period(session, '92')
        assert q.count() == 6
        assert (abs(q[0][0] - Decimal(28.25))) < 0.01
        assert q[0][1] == date.today()
        assert q[0][2] == '92'
        assert q[0][3] == 'okko'

    def test_query_avg_price_period_with_date(self):
        cur_date = date.today() - timedelta(days=1)
        q = query_avg_price_period(session, '92', cur_date, date.today())
        assert q.count() == 4
        assert (abs(q[0][0] - Decimal(28.25))) < 0.01
        assert q[0][1] == date.today()
        assert q[0][2] == '92'
        assert q[0][3] == 'okko'

    def test_query_avg_price_period_no_info(self):
        q = query_avg_price_period(session, '92', date.today() + timedelta(days=2), date.today() + timedelta(days=3))
        assert q.count() == 0


class TestQueryAllPricePeriod:
    def test_query_all_price_period_without_date(self):
        q = query_all_price_period(session)
        assert q.count() == 40
        max_date = datetime(date.today().year, date.today().month, date.today().day, 10, 40)
        assert q[0]==(28, max_date, '92', 'address1', 'okko')

    def test_query_all_price_period_with_date(self):
        cur_date = date.today() - timedelta(days=1)
        q = query_all_price_period(session, cur_date, date.today())
        assert q.count() == 24
        assert q[0] == (28, datetime(date.today().year, date.today().month, date.today().day, 10, 40), '92', 'address1', 'okko')

    def test_query_avg_price_period_no_info(self):
        q = query_all_price_period(session, date.today() + timedelta(days=2), date.today() + timedelta(days=3))
        assert q.count() == 0
