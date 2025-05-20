from rest_framework import serializers
from core.authentication.models import User
from core.authentication.serializers.handlers import (
    get_driver_data, 
    validate_unique_user_email, 
    validate_unique_user_name, 
    validate_unique_username, 
    validate_max_age
)

class UserSerializer(serializers.ModelSerializer):
    driver_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__" 
        extra_fields = ['driver_data']  

    def get_driver_data(self, obj):
        return get_driver_data(self=self, obj=obj)

class UserWriterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)
    passage_id = serializers.CharField(max_length=255)
    data_of_birth = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        validate_unique_user_email(attrs["email"])
        validate_unique_user_name(attrs["name"])
        validate_unique_username(attrs["username"])
        validate_max_age(attrs["data_of_birth"])

        return attrs

class UserReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)
    passage_id = serializers.CharField(max_length=255)
    data_of_birth = serializers.DateField(required=False, allow_null=True)
