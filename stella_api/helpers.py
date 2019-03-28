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
    result_dict = {}
    for row in result:
        row_dict = row._asdict()
        from pprint import pprint
        pprint(row_dict)
        key = row_dict['date_of_price'].strftime('%Y-%m-%d %H:%M')
        if result_dict.get(key) is None:
            result_dict[key] = {}
        result_dict[key]['fuel_company_name'] = row_dict['fuel_company_name']
        result_dict[key]['address'] = row_dict['address']
        result_dict[key][row_dict['fuel_type']] = row_dict['price']
    for key in result_dict.keys():
        name = result_dict[key].pop('fuel_company_name')
        address = result_dict[key].pop('address')
        string = f"{name}\n{address}\n"
        for fuel in result_dict[key].items():
            string += f"{fuel[0]}: {str(fuel[1])} uah\n"
        string += f"price on {key}\n\n"
        result_list.append(string)
    return result_list
