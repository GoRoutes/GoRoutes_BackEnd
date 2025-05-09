from rest_framework import serializers

from core.authentication.serializers.user import UserSerializer

from core.authentication.models import Driver


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = ['id', 'user', 'cnh', 'active']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.update(UserSerializer(), instance=instance.user, validated_data=user_data)
        instance.user = user
        instance.save()
        return instance
