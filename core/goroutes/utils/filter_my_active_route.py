# core/goroutes/utils.py
from rest_framework.views import APIView
from rest_framework.response import Response
from core.goroutes.models import Route
from core.goroutes.serializers.infra import  RouteRetrieveSerializer

class FilterDriverByIsActiveRoutes(APIView):
    def get(self, request, driver_id):
        active_routes = Route.objects.filter(driver_id=driver_id, is_active=True)
        routes_data = RouteRetrieveSerializer(active_routes, many=True).data

        return Response(routes_data)
