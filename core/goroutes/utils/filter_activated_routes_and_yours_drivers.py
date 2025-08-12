# core/goroutes/utils.py
from rest_framework.views import APIView
from rest_framework.response import Response
from core.goroutes.models import Route
from core.goroutes.serializers.infra import RouteActiveSerializer

class FilterDriverByIsActiveRoutes(APIView):
    def get(self, request):
        active_routes = Route.objects.filter(is_active=True)
        routes_data = RouteActiveSerializer(active_routes, many=True).data

        return Response(routes_data)
