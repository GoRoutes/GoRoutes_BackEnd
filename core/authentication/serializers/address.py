from rest_framework import serializers
from core.authentication.models import Address

class AddressReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=10)
    complement = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)

class AddressWriterSerializer(serializers.Serializer):
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=10)
    complement = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)