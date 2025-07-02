from core.goroutes.models import Route
from core.goroutes.serializers import RouteWriteSerializer, RouteReadSerializer
from rest_framework.response import Response
from rest_framework import status

def list_routes(request):
    """
    List all routes.
    """
    routes = Route.objects.all()
    serializer = RouteReadSerializer(routes, many=True)
    return Response(serializer.data)


def create_route(request):
    serializer = RouteWriteSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        route = Route.objects.create(
            name=data["name"],
            origin=data.get("origin", ""),
            destination=data.get("destination", ""),
            distance=data["distance"],
            init_hour=data.get("init_hour"),
            end_hour=data.get("end_hour"),
            duration=data.get("duration"),
            latitude_origin=data.get("latitude_origin"),
            longitude_origin=data.get("longitude_origin"),
            latitude_destination=data.get("latitude_destination"),
            longitude_destination=data.get("longitude_destination"),
        )

        return Response(RouteReadSerializer(route).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)