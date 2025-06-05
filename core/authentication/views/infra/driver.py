from rest_framework.viewsets import ViewSet

from core.authentication.views.handlers import (
    list_drivers, 
    retrieve_driver,
    create_driver,
    delete_driver
)

class DriverViewSet(ViewSet):
    """
    ViewSet para gerenciar motoristas.
    Permite listar, criar motoristas.
    """ 

    def list(self, request):
        return list_drivers(request)

    def retrieve(self, request, pk=None):
        return retrieve_driver(request, pk)

    def create(self, request):
        return create_driver(request)

    def destroy(self, request, pk=None):
        return delete_driver(request, pk)
