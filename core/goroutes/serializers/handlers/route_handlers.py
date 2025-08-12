import requests
from django.conf import settings

def prepare_route_data(route):
    """
    Prepares the route data for serialization.
    """
    return route