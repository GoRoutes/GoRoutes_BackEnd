from rest_framework import serializers

from core.authentication.serializers.user import UserSerializer
from core.authentication.models import Driver


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = ['id', 'user', 'cnh', 'active']
        read_only_fields = ['id', 'user.id', 'user.password']