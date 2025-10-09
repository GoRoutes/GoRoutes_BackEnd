from rest_framework import serializers
from core.authentication.models import Address

class AddressWriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def create(self, validated_data):
        from core.goroutes.utils import get_latitude_longitude
        street = validated_data.get('street', '')
        number = validated_data.get('number', '')
        city = validated_data.get('city', '')
        state = validated_data.get('state', '')
        neighborhood = validated_data.get('neighborhood', '')
        
        def format_neighborhood(name):
            if not name:
                return ''
            words = name.split()
            formatted_words = [word.capitalize() for word in words]
            return ' '.join(formatted_words)

        validated_data['neighborhood'] = format_neighborhood(neighborhood)

        # Construir endereço completo
        full_address = f"{street}, {number} - {city}, {state}"
        
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
