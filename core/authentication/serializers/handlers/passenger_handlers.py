from core.authentication.models import Passenger

def get_passenger_data(self, obj):
        try:
            from core.authentication.serializers.infra import PassengerReadSerializer 
            passenger = obj.passenger
            data = PassengerReadSerializer(passenger).data
            data.pop('user', None)
            return data
        except Passenger.DoesNotExist:
            return None