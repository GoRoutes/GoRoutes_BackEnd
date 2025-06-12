from rest_framework import serializers
from core.authentication.serializers.infra import PassengerReadSerializer, UserReadSerializer, UserWriterSerializer

class ResponsibleCreateSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=11)
    user = UserWriterSerializer()

class ResponsibleReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cpf = serializers.CharField()
    user = UserReadSerializer()
