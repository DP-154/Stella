import os
from googleplaces import GooglePlaces, types, lang
from math import ceil


def get_query_result(lat, lng, radius):
    google_places = GooglePlaces(os.environ['api_google_key'])
    query_result = google_places.nearby_search(
        location='Dnipro, Ukraine', lat_lng={'lat': lat, 'lng': lng},
        radius=radius, types=[types.TYPE_GAS_STATION], language=lang.UKRANIAN)
    return query_result.places

def gas_format(string):
    dic = {
        'азс':    '',
        'сервіс': '',
        'авиас':  'авіас',
        'плюс':   '',
        'avias':  'авіас',
        '-нафта': '',
        'yukon': 'юкон',
        'service': ''

    }
    string = string.lower().strip()
    for word in dic.keys():
        string = string.replace(word, dic[word]).strip()
    string = string.capitalize()
    return string


def get_gas_staton_info_from_google(lat, lng, radius=50):
    res_list = []
    query_result = None
    while not query_result:
        query_result = get_query_result(lat, lng, radius)
        radius += 100
    for place in query_result:
        place.get_details()
        address = place.formatted_address.split(', ')
        if len(address[0]) <= 2:
            address.pop(0)
        if "Дніпро" in address[0] and len(query_result) > 1:
            continue
        address[0] = address[0].replace('вулиця', 'вул.')
        address[0] = address[0].replace('проспект', 'пр.')
        name = gas_format(place.name)
        if not name:
            continue
        res_list.append({
            'name': name,
            'address': address[0] + ', ' + address[1],
            'lat': place.geo_location['lat'],
            'lng': place.geo_location['lng']
        })
    return res_list


def pagination_output(stringlist, position, step):
    start_pos = position
    string = ""
    limit = len(stringlist)
    for i in range(step):
        if position >= limit:
            position = start_pos + step
            break
        string += stringlist[position]
        position += 1
    curr_page = position // step
    pageall = ceil(limit / step)
    string += f" --- page #{curr_page} of {pageall} ---"
    return string, position
