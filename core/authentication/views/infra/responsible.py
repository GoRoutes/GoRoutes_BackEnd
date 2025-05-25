from rest_framework.viewsets import ViewSet
from core.authentication.views.handlers.responsible_handlers import (
    list_responsibles,
    retrieve_responsible,
    create_responsible
)

class ResponsibleViewSet(ViewSet):
    def list(self, request):
        return list_responsibles(request)

    def retrieve(self, request, pk=None):
        return retrieve_responsible(request, pk)

    def create(self, request):
        return create_responsible(request)
