from rest_framework import serializers
from core.authentication.models import User
from core.authentication.models import Driver

class UserSerializer(serializers.ModelSerializer):
    driver_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__" 
        extra_fields = ['driver_data']  

    def get_driver_data(self, obj):
        try:
            from .driver import DriverReadSerializer 
            driver = obj.driver
            data = DriverReadSerializer(driver).data
            data.pop('user', None)
            return data
        except Driver.DoesNotExist:
            return None

class UserWriterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)
    passage_id = serializers.CharField(max_length=255)
    data_of_birth = serializers.DateField(required=False, allow_null=True)

class UserReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)
    passage_id = serializers.CharField(max_length=255)
    data_of_birth = serializers.DateField(required=False, allow_null=True)
