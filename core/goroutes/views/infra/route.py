from rest_framework import viewsets
from core.goroutes.views.handlers import (
    list_routes,
    create_route
)

class RouteViewSet(viewsets.ViewSet):
    """
    ViewSet for handling routes.
    """
    
    def list(self, request):
        return list_routes(request)

    def create(self, request):
        return create_route(request)
