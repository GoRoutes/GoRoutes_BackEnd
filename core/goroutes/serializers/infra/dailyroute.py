from operator import is_
from django.conf import settings
from rest_framework import serializers
from core.authentication.models import Passenger
from core.goroutes.models import Route
from core.goroutes.models import PassengerRoute, Presence
from core.goroutes.serializers import VehicleSerializer
from core.authentication.serializers.infra import DriverReadSerializer
import requests

from rest_framework import serializers
from core.goroutes.models import DailyRoute, Route
from core.authentication.models import Passenger
from core.goroutes.serializers import VehicleSerializer
from core.authentication.serializers.infra import DriverReadSerializer

class DailyRouteWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    passengers_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all()),
        required=False,
        allow_empty=True
    )
    original = serializers.BooleanField(default=True)

    def prepare_route_of_father_route(self, route):
        from core.goroutes.serializers.handlers import get_data_of_route

        route_data = get_data_of_route(route.id)

        # Substitui a lista de passageiros do pai pela do serializer
        passengers = self.validated_data.get("passengers_list", [])
        route_data["passengers_list"] = [p.id for p in passengers]
        route_data["original"] = self.validated_data.get("original", True)

        return route_data


class PresenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Presence.Status.choices)
    passenger_route = serializers.PrimaryKeyRelatedField(queryset=Passenger.objects.all())
    daily_route = serializers.PrimaryKeyRelatedField(queryset=DailyRoute.objects.all())
    passenger_name = serializers.SerializerMethodField()
    address_passenger = serializers.SerializerMethodField()
    responsible_passenger = serializers.SerializerMethodField()

    def get_passenger_name(self, obj):
        return obj.passenger_route.user.name

    def get_responsible_passenger(self, obj):
        student_data = getattr(obj.passenger_route, "student_data", None)
        if student_data and student_data.responsible:
            return student_data.responsible.id
        return None

    def get_address_passenger(self, obj):
        from core.goroutes.utils import get_latitude_longitude
        addresses = obj.passenger_route.address.all()
        main_address = addresses.filter(is_main=True)
        results = []
        for addr in main_address:
            addr_str = str(addr)
            lat, lng = get_latitude_longitude(addr_str)
            results.append({
                "address": addr_str,
                "latitude": lat,
                "longitude": lng
            })
        return results

class DailyRouteListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    init_hour = serializers.TimeField()
    end_hour = serializers.TimeField()
    is_active = serializers.BooleanField()
    vehicle = VehicleSerializer(read_only=True)
    driver = DriverReadSerializer()
    presences = PresenceSerializer(many=True)
    latitude_origin = serializers.FloatField()
    longitude_origin = serializers.FloatField()
    latitude_destination = serializers.FloatField()
    longitude_destination = serializers.FloatField()
    optimized_route_url = serializers.SerializerMethodField()
    overview_polyline = serializers.JSONField()
    finalized = serializers.BooleanField()

    def get_optimized_route_url(self, obj):
        if not obj.optimized_route_url:
            return None
        return obj.optimized_route_url

class DailyRouteRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    init_hour = serializers.TimeField()
    end_hour = serializers.TimeField()
    is_active = serializers.BooleanField()
    vehicle = VehicleSerializer(read_only=True)
    driver = DriverReadSerializer()
    presences = PresenceSerializer(many=True)
    latitude_origin = serializers.FloatField()
    longitude_origin = serializers.FloatField()
    latitude_destination = serializers.FloatField()
    longitude_destination = serializers.FloatField()
    optimized_route_url = serializers.SerializerMethodField()
    overview_polyline = serializers.JSONField()
    finalized = serializers.BooleanField()


    def get_optimized_route_url(self, obj):
        if not obj.optimized_route_url:
            return None
        return obj.optimized_route_url




