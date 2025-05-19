from rest_framework import serializers
from core.authentication.models import User, Address, Driver

class AddressSerializer(serializers.Serializer):
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=10)
    complement = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)
    passage_id = serializers.CharField(max_length=255)
    data_of_birth = serializers.DateField(required=False, allow_null=True)

class DriverCreateSerializer(serializers.Serializer):
    cnh = serializers.CharField(max_length=20)
    cpf = serializers.CharField(max_length=14)
    user = UserSerializer()
    addresses = AddressSerializer(many=True, required=False)

    def validate(self, data):
        return data
    
class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state']

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'telephone', 'passage_id', 'data_of_birth']

class DriverReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()
    adresses = AddressReadSerializer(many=True)

    class Meta:
        model = Driver
        fields = ['id', 'cnh', 'cpf', 'is_active', 'user', 'adresses']
