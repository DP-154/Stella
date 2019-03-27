import os
from geopy.geocoders import Nominatim, GoogleV3
import googlemaps
from googlemaps import places

# TODO: antiduplicate function, that will delete stations with same adresses


def antiduplicate(lst):
    pass


def get_station_by_location(lat, lng):
    gm_client = googlemaps.Client(os.environ['api_google_key'])
    gmap = places.places_nearby(client=gm_client, location={'lat': lat, 'lng': lng}, radius=140)
    geo = GoogleV3(os.environ['api_google_key'])
    res = gmap['results']
    res_list = []
    for i in range(len(res)):
        if 'gas_station' in res[i]['types']:
            name = res[i]['name']
            station_lat = res[i]['geometry']['location']['lat']
            station_lng = res[i]['geometry']['location']['lng']
            adress = str(geo.geocode(f"{station_lat}, {station_lng}")).split(',')
            street = adress[0] + ',' + adress[1]
            res_list.append({
                    'name': name,
                    'adress': street,
                    'lat': station_lat,
                    'lng': station_lng
                    })
    return res_list
