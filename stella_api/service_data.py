from stella_api.image_recognition import digit_to_price
import database.add_data_query(function) as db_add_data_query

def data_put_to_db(data_bot):
    recognized_price=digit_to_price(data_bot.get('dbx_path'))
    rec_data=map(data_bot,recognized_price)
    db_add_data_query(rec_data)


def map(data_bot,recognized_price) -> dict:
    result = {
        'user': data_bot.get('user_id'),
        'gps_location': data_bot.get('gps_location'),
        'gas_station':data_bot.get('gas_station'),
        'fuel_company':data_bot.get('fuel_company'),
        'date_of_price':data_bot.get('date_of_price'),
        'is_recognised':True,
        'image_link':data_bot.get('dbx_path'),
        'fuel': recognized_price[:2],
        'price':float(recognized_price[2:])
    }

    return result

def get_all_company():
    pass

def get_all_station_location():
    pass

def get_all_station_company():
    pass

