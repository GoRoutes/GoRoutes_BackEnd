from rest_framework import viewsets
from core.goroutes.models import Vehicle
from core.goroutes.serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
