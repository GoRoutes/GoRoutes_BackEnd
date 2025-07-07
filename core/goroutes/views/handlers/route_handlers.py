from core.goroutes.models import Route, PassengerRoute
from core.authentication.models import Passenger
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

        # Criação da rota
        route = Route.objects.create(
            name=data["name"],
            origin=data.get("origin", ""),
            destination=data.get("destination", ""),
            distance=data.get("distance", 0.0),
            init_hour=data.get("init_hour"),
            end_hour=data.get("end_hour"),
            duration=data.get("duration"),
            latitude_origin=data.get("latitude_origin"),
            longitude_origin=data.get("longitude_origin"),
            latitude_destination=data.get("latitude_destination"),
            longitude_destination=data.get("longitude_destination"),
        )

        passenger_list = data.get("passengers_list", [])

        for passenger in passenger_list:
            # Garante que estamos lidando com instância e não com ID
            if isinstance(passenger, int):
                try:
                    passenger = Passenger.objects.get(pk=passenger)
                except Passenger.DoesNotExist:
                    continue  # ou trate o erro conforme sua necessidade

            # Evita duplicata
            PassengerRoute.objects.get_or_create(passenger=passenger, route=route)

        return Response(RouteReadSerializer(route).data, status=status.HTTP_201_CREATED)

    # Erro de validação
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
