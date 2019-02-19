import os
from pprint import pprint

from PIL import Image, ExifTags
from GPSPhoto import gpsphoto
from pygeocoder import Geocoder
from geopy.geocoders import Nominatim, GoogleV3
import exifread
from piexif import load, dump
import json

import googlemaps # использовать для google maps and google places
from googlemaps import places

pic = 'someIMG7.jpg'

gps_data = gpsphoto.getGPSData(pic)
# print(gps_data)
print(gps_data['Latitude'], gps_data['Longitude'])

img = Image.open(pic)
exifData = {}
exifDataRaw = img._getexif()
for tag, value in exifDataRaw.items():
    decodedTag = ExifTags.TAGS.get(tag)
    exifData[decodedTag] = value

# pprint(exifData)
#
# lat = gps_data['Latitude']
# long = gps_data['Longitude']

lat = '48.452698'
long = '35.077502'

gm_client = googlemaps.Client(os.environ['api_google_key'])
gmap = places.places_nearby(client=gm_client, location={'lat': '48.453215', 'lng': '35.076644'}, radius=25)


y = gmap['results']

# print(y)


# for i in gmap['results']:
#     for j in i:
#         print(j)

for i in range(len(y)):
    if 'gas_station' in y[i]['types']:
        print(y[i]['name'])
    # print(y[i]['name'])
    # print(y[i]['types'])




# print(o.['result'])


# pprint(gmap.items)

# OKKO coord
# lat = '48.452698'
# long = '35.077502'

# neftek coord 48.453215, 35.076644


# geo = GoogleV3(os.environ['api_google_key'])
# res = str(geo.geocode(f"{lat}, {long}"))
# print(res)
#
# street = res.split(',')
# print(f"{street[0]}, {street[1]}, {street[2]}")
#
# geolocator = Nominatim(user_agent="SStetsPythonGooleMap")
# location = geolocator.geocode(f"{street[0]}, {street[1]}, {street[2]}")
#
# print(location.address)

