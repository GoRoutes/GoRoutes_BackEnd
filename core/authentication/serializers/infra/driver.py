from rest_framework import serializers
from core.authentication.models import Driver
from core.authentication.serializers.infra import (
    AddressReadSerializer, 
    AddressWriterSerializer, 
    UserWriterSerializer, 
    UserReadSerializer
)

class DriverCreateSerializer(serializers.Serializer):
    cnh = serializers.CharField(max_length=20)
    cpf = serializers.CharField(max_length=14)
    user = UserWriterSerializer()
    addresses = AddressWriterSerializer(many=True, required=False)

    def validate(self, data):
        return data

class DriverReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cnh = serializers.CharField(max_length=20)
    cpf = serializers.CharField(max_length=14)
    is_active = serializers.BooleanField()
    user = UserReadSerializer()
    adresses = AddressReadSerializer(many=True)