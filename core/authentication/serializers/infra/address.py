from rest_framework import serializers
from core.authentication.models import Address
from core.goroutes.utils import get_latitude_longitude

class AddressWriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def create(self, validated_data):
        street = validated_data.get('street', '')
        number = validated_data.get('number', '')
        city = validated_data.get('city', '')
        state = validated_data.get('state', '')
        
        # Construir o endereço completo
        full_address = f"{street}, {number} - {city}, {state}"
        
        # Obter latitude e longitude
        data_latitude_longitude = get_latitude_longitude(full_address)
        
        if data_latitude_longitude:
            validated_data['latitude'], validated_data['longitude'] = data_latitude_longitude
        
        return super().create(validated_data)

class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class AddressPassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'full_address')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['full_address'] = f"{instance.street}, {instance.number} - {instance.neighborhood}, {instance.city} - {instance.state}"
        return representation
