import datetime
import decimal
from functools import singledispatch


@singledispatch
def to_serializable(val):
    return str(val)


@to_serializable.register(datetime.datetime)
def ts_datetime(val):
    return val.isoformat()


@to_serializable.register(decimal.Decimal)
def ts_decimal(val):
    return float(val)


def query_to_dict(result):
    result_dict = {}
    num = 1
    for row in result:
        row_dict = row._asdict()
        result_dict[f'row {num}'] = row_dict
        num += 1
    return result_dict
