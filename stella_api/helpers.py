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

def query_to_list(result):
    result_list = []
    for row in result:
        row_dict = row._asdict()
        string = f"{row_dict['fuel_company_name']}\n{row_dict['address']}\nA{row_dict['fuel_type']}: {row_dict['price']} uah\n" \
            f"price on {row_dict['date_of_price'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        result_list.append(string)
    return result_list
