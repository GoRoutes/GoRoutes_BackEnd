from rest_framework import serializers
from core.authentication.models import Address

from core.authentication.serializers.handlers import validate_states
from core.goroutes.serializers.handlers import get_latitude_longitude
class AddressReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=10)
    complement = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)
    is_main = serializers.BooleanField(default=False)
    full_address = serializers.SerializerMethodField()
    latitude = serializers.CharField(max_length=20, allow_null=True, required=False, allow_blank=True)
    longitude = serializers.CharField(max_length=20, allow_null=True, required=False, allow_blank=True)

    def get_full_address(self, obj):
        full_address = f'{obj.street}, {obj.number}, {obj.neighborhood}, {obj.city}, {obj.state}'
        return full_address
    
    

class AddressWriterSerializer(serializers.Serializer):
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=10)
    complement = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)
    is_main = serializers.BooleanField(default=False)
    latitude = serializers.CharField(max_length=20, allow_null=True, required=False, allow_blank=True)
    longitude = serializers.CharField(max_length=20, allow_null=True, required=False, allow_blank=True)

    def validate(self, attrs):
        validate_states(attrs["state"])

        full_address = f'{attrs["street"]}, {attrs["number"]}, {attrs["neighborhood"]}, {attrs["city"]}, {attrs["state"]}'

        data_latitude_longitude = get_latitude_longitude(full_address)

        attrs["latitude"] = data_latitude_longitude.get("latitude")
        attrs["longitude"] = data_latitude_longitude.get("longitude")

        return attrs
