from django.conf import settings
from rest_framework import serializers
from core.authentication.models import Passenger
from core.goroutes.models import Route, PassengerRoute, Vehicle
from urllib.parse import quote_plus
import json

class RouteWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    distance = serializers.FloatField(required=False, default=0.0)
    init_hour = serializers.TimeField()
    end_hour = serializers.TimeField()
    duration = serializers.FloatField(required=False, default=0.0)
    passengers_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all()), 
        required=False, 
        allow_empty=True
    )
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        required=False,
        allow_null=True
    )
    auto_recalculate = serializers.BooleanField(default=False)
    addresses = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    addresses_order = serializers.JSONField(required=False)
    optimized_route_url = serializers.URLField(required=False, allow_blank=True)

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
    markers = serializers.JSONField()
    optimized_route_url = serializers.SerializerMethodField()
    vehicle = serializers.PrimaryKeyRelatedField(read_only=True)
    auto_recalculate = serializers.BooleanField()
    addresses = serializers.ListField(child=serializers.CharField())
    addresses_order = serializers.JSONField()
    overview_polyline = serializers.JSONField()
    points = serializers.JSONField()
    coords_passageiros = serializers.JSONField()

    def get_passengers(self, obj):
        from core.authentication.serializers.infra import PassengerRouteReadSerializer

        passenger_routes = PassengerRoute.objects.filter(route=obj)
        passengers = [pr.passenger for pr in passenger_routes]
        return PassengerRouteReadSerializer(passengers, many=True).data

    # def get_markers(self, obj):
    #     passenger_routes = PassengerRoute.objects.filter(route=obj)
    #     passengers = [pr.passenger for pr in passenger_routes]

    #     addresses = []
    #     for passenger in passengers:
    #         if hasattr(passenger, 'address'):
    #             addresses.extend(passenger.address.filter(is_main=True))

    #     from core.authentication.serializers.infra import AddressReadSerializer
    #     return AddressReadSerializer(addresses, many=True).data

    def get_optimized_route_url(self, obj):
        if not obj.optimized_route_url:
            return None
        return obj.optimized_route_url
