from rest_framework import serializers
from core.goroutes.serializers.handlers import prepare_route_data

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

    def validate(self, attrs):
        """
        Validate the route data.
        """
        return prepare_route_data(attrs)
    
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