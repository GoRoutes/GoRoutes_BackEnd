from rest_framework.views import APIView
from rest_framework.response import Response
from core.goroutes.models import Route
from core.goroutes.serializers.infra import RouteReadSerializer

class FilterMyDriverRoutes(APIView):
    def get(self, request, driver_id):
        driver_routes = Route.objects.filter(driver_id=driver_id)
        routes_data = RouteReadSerializer(driver_routes, many=True).data

        return Response(routes_data)
