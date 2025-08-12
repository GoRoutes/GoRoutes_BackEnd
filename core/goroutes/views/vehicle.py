from rest_framework import viewsets, status
from rest_framework.response import Response
from core.goroutes.models import Vehicle
from core.goroutes.serializers import VehicleSerializer
from core.uploader.utils.create_image import create_image

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer