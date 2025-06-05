from rest_framework.viewsets import ViewSet
from rest_framework.mixins import CreateModelMixin
from core.authentication.views.handlers import (
    list_responsibles,
    retrieve_responsible,
    create_responsible, 
    delete_responsible
)

class ResponsibleViewSet(ViewSet, CreateModelMixin):
    def list(self, request):
        return list_responsibles(request)

    def retrieve(self, request, pk=None):
        return retrieve_responsible(request, pk)

    def create(self, request):
        return create_responsible(request)
    
    def destroy(self, request, pk=None):
        return delete_responsible(request, pk)
