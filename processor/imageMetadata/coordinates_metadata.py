import os

from googleplaces import GooglePlaces, types, lang


def gasStationInfo(lat, long, start_radius=25, radius_limit=None):
    google_places = GooglePlaces(os.environ['api_google_key'])
    res_list = []
    if radius_limit is None:
        limit = 100
    else:
        limit = radius_limit
    while start_radius <= limit:
        start_radius += 25
        query_result = google_places.nearby_search(
            location='Dnipro, Ukraine', lat_lng={'lat': lat, 'lng': long},
            radius=start_radius, types=[types.TYPE_GAS_STATION], language=lang.UKRANIAN)

        for place in query_result.places:
            place.get_details()
            res_list.append({
                'name': place.name,
                'adress': place.formatted_address,
                'geo_location': place.geo_location,
                'place_id': place.place_id,
                'website': place.website,
                'local_phone_number': place.local_phone_number,
                'international_phone_number': place.international_phone_number,
                'rating': place.rating
            })
            if radius_limit is None:
                return res_list
    return res_list
