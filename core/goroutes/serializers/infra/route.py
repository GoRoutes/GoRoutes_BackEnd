from django.conf import settings
from rest_framework import serializers
from core.goroutes.serializers.handlers import prepare_route_data
from core.authentication.models import Passenger
from core.goroutes.models import Route, PassengerRoute
from urllib.parse import quote_plus
import json
from sklearn.cluster import KMeans
from typing import List, Dict, Any

class RouteWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    origin = serializers.CharField(max_length=255, required=False, allow_blank=True)
    destination = serializers.CharField(max_length=255, required=False, allow_blank=True)
    distance = serializers.FloatField()
    init_hour = serializers.TimeField(required=False, allow_null=True)
    end_hour = serializers.TimeField(required=False, allow_null=True)
    duration = serializers.FloatField(required=False, allow_null=True)
    latitude_origin = serializers.FloatField(required=False, allow_null=True)
    longitude_origin = serializers.FloatField(required=False, allow_null=True)
    latitude_destination = serializers.FloatField(required=False, allow_null=True)
    longitude_destination = serializers.FloatField(required=False, allow_null=True)
    passengers_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all()), 
        required=False, 
        allow_empty=True
    )

    def validate(self, attrs):
        """
        Validate the route data.
        """
        return prepare_route_data(attrs)
    
from urllib.parse import urlencode, quote_plus

class RouteReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    distance = serializers.FloatField()
    init_hour = serializers.TimeField()
    end_hour = serializers.TimeField()
    duration = serializers.FloatField()
    latitude_origin = serializers.FloatField()
    longitude_origin = serializers.FloatField()
    latitude_destination = serializers.FloatField()
    longitude_destination = serializers.FloatField()
    passengers = serializers.SerializerMethodField()
    markers = serializers.SerializerMethodField()
    optimized_route_url = serializers.SerializerMethodField()

    def get_passengers(self, obj):
        from core.authentication.serializers.infra import PassengerRouteReadSerializer

        passenger_routes = PassengerRoute.objects.filter(route=obj)
        passengers = [pr.passenger for pr in passenger_routes]
        return PassengerRouteReadSerializer(passengers, many=True).data

    def get_markers(self, obj):
        passenger_routes = PassengerRoute.objects.filter(route=obj)
        passengers = [pr.passenger for pr in passenger_routes]

        addresses = []
        for passenger in passengers:
            if hasattr(passenger, 'address'):
                addresses.extend(passenger.address.filter(is_main=True))

        from core.authentication.serializers.infra import AddressReadSerializer
        return AddressReadSerializer(addresses, many=True).data

    def get_optimized_route_url(self, obj):
        from urllib.parse import urlencode, quote_plus

        origin = quote_plus(obj.origin)
        destination = quote_plus(obj.destination)

        passenger_routes = PassengerRoute.objects.filter(route=obj)
        passengers = [pr.passenger for pr in passenger_routes]

        waypoints = []
        for passenger in passengers:
            if hasattr(passenger, 'address'):
                main_addresses = passenger.address.filter(is_main=True)
                waypoints.extend([addr.full_address for addr in main_addresses])

        if not waypoints:
            return None

        base_url = "https://www.google.com/maps/dir/?"

        waypoints_str = "|".join(waypoints)

        params = {
            "api": "1",
            "origin": obj.origin,
            "destination": obj.destination,
            "waypoints": waypoints_str,
        }

        url = base_url + urlencode(params, safe='|')

        return url
