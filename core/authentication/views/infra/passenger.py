from rest_framework.viewsets import ViewSet

from core.authentication.views.handlers import (
    list_passengers,
    retrieve_passenger,
    create_passenger
)

class PassengerViewSet(ViewSet):
    """
    ViewSet para gerenciar passageiros.
    Permite listar, criar passageiros.
    """ 

    def list(self, request):
        return list_passengers(request)

    def retrieve(self, request, pk=None):
        return retrieve_passenger(request, pk)

    def create(self, request):
        return  create_passenger(request)
