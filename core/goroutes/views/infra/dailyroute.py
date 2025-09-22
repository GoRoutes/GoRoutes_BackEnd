from rest_framework import viewsets
from core.goroutes.views.handlers import (
    create_dailyroute, 
    list_dailyroutes, 
    retrieve_dailyroute
)


class DailyRouteViewSet(viewsets.ViewSet):
    """
    ViewSet para DailyRoute
    """
    def create(self, request):
        return create_dailyroute(request)

    def list(self, request):
        return list_dailyroutes(request)
    
    def retrieve(self, request, pk=None):
        return retrieve_dailyroute(request, pk)