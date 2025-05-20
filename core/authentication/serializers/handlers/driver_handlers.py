from core.authentication.models import Driver

def get_driver_data(self, obj):
        try:
            from core.authentication.serializers.infra import DriverReadSerializer 
            driver = obj.driver
            data = DriverReadSerializer(driver).data
            data.pop('user', None)
            return data
        except Driver.DoesNotExist:
            return None