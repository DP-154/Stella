import os
from pprint import pprint

from PIL import Image, ExifTags
from GPSPhoto import gpsphoto
from pygeocoder import Geocoder
from geopy.geocoders import Nominatim, GoogleV3
import exifread
from piexif import load, dump
import json
import googlemaps
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


# OKKO coord
# lat = '48.452698'
# long = '35.077502'

# neftek coord
# lat = '48.453215'
# long = '35.076644'

lat = '48.453215'
long = '35.076644'

gm_client = googlemaps.Client(os.environ['api_google_key'])
gmap = places.places_nearby(client=gm_client, location={'lat': '48.453215', 'lng': '35.076644'}, radius=25)
res = gmap['results']

for i in range(len(res)):
    if 'gas_station' in res[i]['types']:
        print(res[i]['name'])

geo = GoogleV3(os.environ['api_google_key'])
res = str(geo.geocode(f"{lat}, {long}"))
street = res.split(',')

geolocator = Nominatim(user_agent="SStetsPythonGooleMap")
location = geolocator.geocode(f"{street[0]}, {street[1]}, {street[2]}")
print(location.address)

