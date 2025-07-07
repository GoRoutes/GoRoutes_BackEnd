import requests
from django.conf import settings
api_key = settings.GOOGLE_MAPS_API_KEY

def prepare_route_data(route):
    """
    Prepares the route data for serialization.
    """
    origin = route["origin"]
    destination = route["destination"]
    init_hour = route["init_hour"]
    end_hour = route["end_hour"]

    locale_origin = get_latitude_longitude(origin)
    locale_destination = get_latitude_longitude(destination)
    duration = get_distance_and_duration(origin, destination)["duration"]
    distance = get_distance_and_duration(origin, destination)["distance"] 
    
    return {
        'name': route["name"],
        'origin': origin,
        'destination': destination,
        'latitude_origin': locale_origin['latitude'] if locale_origin else None,
        'longitude_origin': locale_origin['longitude'] if locale_origin else None,
        'latitude_destination': locale_destination['latitude'] if locale_destination else None,
        'longitude_destination': locale_destination['longitude'] if locale_destination else None,
        'distance': distance if distance else None,
        'init_hour': init_hour,
        'end_hour': end_hour,
        'duration': duration if duration else None,
        'passengers_list': route.get("passengers_list", [])
    }

def get_latitude_longitude(address):
    """
    Fetches latitude and longitude for a given address using Google Maps API.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return {'latitude': location['lat'], 'longitude': location['lng']}

    return None

def get_distance_and_duration(origin, destination):

    api_key = settings.GOOGLE_MAPS_API_KEY
    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "key": api_key
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['rows']:
            elements = data['rows'][0]['elements']
            if elements:
                distance = elements[0]['distance']['value']
                duration = elements[0]['duration']['value']
                return {'distance': distance, 'duration': duration}

    return None