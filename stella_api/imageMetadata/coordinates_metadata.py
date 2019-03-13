import os
from geopy.geocoders import Nominatim, GoogleV3
import googlemaps
from googlemaps import places


class MetaDataFromCoordinates:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def get_name(self):
        gm_client = googlemaps.Client(os.environ['api_google_key'])
        gmap = places.places_nearby(client=gm_client, location={'lat': self.lat, 'lng': self.long}, radius=25)
        res = gmap['results']
        for i in range(len(res)):
            if 'gas_station' in res[i]['types']:
                name = res[i]['name']
                return name

    def get_address(self):
        geo = GoogleV3(os.environ['api_google_key'])
        res = str(geo.geocode(f"{self.lat}, {self.long}"))
        street = res.split(',')
        geolocator = Nominatim(user_agent=os.environ['google_user_agent'])
        location = geolocator.geocode(f"{street[0]}, {street[1]}, {street[2]}")
        return location.address


if __name__ == '__main__':
    lat = '48.453215'
    long = '35.076644'
    a = MetaDataFromCoordinates(lat, long)

    print(a.get_address())
    print(a.get_name())




