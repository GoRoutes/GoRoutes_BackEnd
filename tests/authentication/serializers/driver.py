from rest_framework import serializers

from core.authentication.serializers.infra.user import UserSerializer

from core.authentication.models import Driver


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = ['id', 'user', 'cnh', 'active']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        driver = Driver.objects.create(user=user, **validated_data)
        return driver
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        instance.user = user
        instance.save()
        return instance
