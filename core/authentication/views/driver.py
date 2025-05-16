from rest_framework import viewsets

from core.authentication.models import Driver
from core.authentication.serializers import DriverSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
