from rest_framework import viewsets
from core.goroutes.models import Notify
from core.goroutes.serializers import NotifySerializer

class NotifyViewSet(viewsets.ModelViewSet):
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer
