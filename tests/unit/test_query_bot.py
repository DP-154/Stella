from datetime import datetime, date
from decimal import Decimal
from os import environ

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db_query_bot import query_by_station_min_price, query_avg_all_stations, \
    query_by_station_current_date, days_to_date, query_avg_price_period

TEST_CONNECT = environ['DATABASE_TEST_URL']

engine = create_engine(TEST_CONNECT)
SessionMaker = sessionmaker(bind=engine)

session = SessionMaker()


class TestDaysToDate:
    def test_days_to_date_date(self):
        assert days_to_date(datetime(2019, 3, 4).date()) == datetime(2019, 3, 4).date()

    def test_days_to_date_datetime(self):
        assert days_to_date(datetime(2019, 3, 4)) == datetime(2019, 3, 4).date()

    def test_days_to_date_string_positive(self):
        assert days_to_date('2019-03-04') == datetime(2019, 3, 4).date()

    def test_days_to_date_string_wrong_format(self):
        assert days_to_date('04.03.2019') is None

    def test_days_to_date_empty(self):
        assert days_to_date(None) is None


class TestQueryByStationCurrentDate:

    def test_query_by_station_current_date_max_date(self):
        q = query_by_station_current_date(session, 'okko', 'address1')
        assert q.count() == 2
        assert q[0] == (pytest.approx(28, 0.01), 'address1', datetime(2019, 3, 5, 10, 40),'92')

    def test_query_by_station_current_date_with_date(self):
        q = query_by_station_current_date(session, 'okko', 'address1', datetime(2019, 3, 4))
        assert q.count() == 4
        assert (abs(q[0][0] - Decimal(28.2))) < 0.01
        assert q[0][2] == datetime(2019, 3, 4, 22, 39)
        assert q[0][3] == '92'

    def test_query_by_station_current_date_no_data(self):
        q = query_by_station_current_date(session, 'okko', 'address1', datetime(2019, 3, 8))
        assert q.count() == 0

class TestQueryAVGAllStation:
    def test_query_avg_all_stations_max_date(self):
        q = query_avg_all_stations(session)
        assert q.count() == 2
        assert (abs(q[0][0] - Decimal(28.38))) < 0.01
        assert q[0][1] == '92'
        assert q[0][2] == datetime.strptime('2019-03-05', '%Y-%m-%d').date()

    def test_query_avg_all_stations_with_date(self):
        q = query_avg_all_stations(session, '2019-03-04')
        assert q.count() == 2
        assert (abs(q[0][0] - Decimal(28.68))) < 0.01
        assert q[0][1] == '92'
        assert q[0][2] == datetime.strptime('2019-03-04', '%Y-%m-%d').date()

    def test_query_avg_all_stations_no_data(self):
        q = query_avg_all_stations(session, '2019-03-08')
        assert q.count() == 0


class TestQueryByStationMinPrice:
    def test_query_by_station_min_price_max_date(self):
        q = query_by_station_min_price(session, '95')
        assert q[0] == (30, datetime(2019, 3, 5, 10, 40),'95','address1','okko')

    def test_query_by_station_min_price_with_date(self):
        q = query_by_station_min_price(session, '95', datetime(2019, 3, 4).date())
        assert (abs(q[0][0] - Decimal(30.2))) < 0.01
        assert q[0][1] == datetime(2019, 3, 4, 22, 39)
        assert q[0][2] == '95'
        assert q[0][3] == 'address1'
        assert q[0][4] == 'okko'

    def test_query_by_station_min_price_no_data(self):
        q = query_by_station_min_price(session, '95','2019-03-08')
        assert q.count() == 0

class TestQueryAVGPricePeriod:
    def test_query_avg_price_period_without_date(self):
        q = query_avg_price_period(session,'92')
        assert q.count() == 6
        assert (abs(q[0][0] - Decimal(28.95))) < 0.01
        assert q[0][1] == '92'
        assert q[0][2] == date(2019, 3, 3)
        assert q[0][3] == 'okko'

    def test_query_avg_price_period_with_date(self):
        q = query_avg_price_period(session, '92', date(2019, 3, 4), date(2019, 3, 5))
        assert q.count() == 4
        assert (abs(q[0][0] - Decimal(28.55))) < 0.01
        assert q[0][1] == '92'
        assert q[0][2] == date(2019, 3, 4)
        assert q[0][3] == 'okko'

    def test_query_avg_price_period_no_date(self):
        q = query_avg_price_period(session, '92', date(2019, 3, 7), date(2019, 3, 9))
        assert q.count() == 0

session.close()


