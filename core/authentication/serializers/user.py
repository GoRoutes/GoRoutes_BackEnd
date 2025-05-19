from rest_framework import serializers
from core.authentication.models import User
from core.authentication.models import Driver
from core.authentication.serializers import DriverReadSerializer  

class UserSerializer(serializers.ModelSerializer):
    driver_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__" 
        extra_fields = ['driver_data']  

    def get_driver_data(self, obj):
        try:
            driver = obj.driver
            data = DriverReadSerializer(driver).data
            data.pop('user', None)
            return data
        except Driver.DoesNotExist:
            return None
