from rest_framework import viewsets
from core.goroutes.views.handlers import (
    list_routes,
    create_route, 
    retrieve_route
)

class RouteViewSet(viewsets.ViewSet):
    """
    ViewSet for handling routes.
    """
    
    def list(self, request):
        return list_routes(request)

    def create(self, request):
        return create_route(request)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific route by its primary key.
        """
        return retrieve_route(request, pk)