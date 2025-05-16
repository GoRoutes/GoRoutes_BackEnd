from rest_framework import viewsets

from core.authentication.models import Parent
from core.authentication.serializers import ParentListSerializer, ParentSerializer


class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return ParentListSerializer
        return super().get_serializer_class()
