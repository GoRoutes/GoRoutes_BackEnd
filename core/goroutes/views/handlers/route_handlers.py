from core.goroutes.models import Route, PassengerRoute
from core.authentication.models import Passenger
from core.goroutes.serializers import RouteWriteSerializer, RouteReadSerializer
from rest_framework.response import Response
from rest_framework import status
from core.goroutes.utils import get_latitude_longitude
from django.db import transaction
from django.db.models import signals

def list_routes(request):
    """
    List all routes.
    """
    routes = Route.objects.all()
    serializer = RouteReadSerializer(routes, many=True)
    return Response(serializer.data)

@transaction.atomic
def create_route(request):
    serializer = RouteWriteSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        # Obter coordenadas do endereço de origem
        origin_lat, origin_lng = get_latitude_longitude(data["origin"])
        if not origin_lat or not origin_lng:
            return Response(
                {"error": "Não foi possível obter as coordenadas do endereço de origem"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obter coordenadas do endereço de destino
        dest_lat, dest_lng = get_latitude_longitude(data["destination"])
        if not dest_lat or not dest_lng:
            return Response(
                {"error": "Não foi possível obter as coordenadas do endereço de destino"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Criação da rota (inicialmente sem auto_recalculate)
        route = Route.objects.create(
            name=data["name"],
            origin=data["origin"],
            destination=data["destination"],
            distance=data.get("distance", 0.0),
            init_hour=data["init_hour"],
            end_hour=data["end_hour"],
            duration=data.get("duration", 0.0),
            latitude_origin=origin_lat,
            longitude_origin=origin_lng,
            latitude_destination=dest_lat,
            longitude_destination=dest_lng,
            auto_recalculate=False,  # Inicialmente falso
            addresses=data.get("addresses", []),
            vehicle=data.get("vehicle"),
            addresses_order=data.get("addresses_order", []),
            optimized_route_url=data.get("optimized_route_url", "")
        )

        # Criar PassengerRoute para cada passageiro
        passenger_list = data.get("passengers_list", [])
        for passenger in passenger_list:
            # Garante que estamos lidando com instância e não com ID
            if isinstance(passenger, int):
                try:
                    passenger = Passenger.objects.get(pk=passenger)
                except Passenger.DoesNotExist:
                    continue  # ou trate o erro conforme sua necessidade

            # Evita duplicata
            PassengerRoute.objects.create(passenger=passenger, route=route)

        # Agora que os PassengerRoute foram criados, ativar auto_recalculate e tentar salvar
        route.auto_recalculate = True
        
        # Chamar o signal manualmente para verificar se a otimização foi bem sucedida
        signal_response = signals.pre_save.send(
            sender=Route,
            instance=route,
            raw=False,
            using='default',
            update_fields=None
        )
        
        # Verificar se algum receiver retornou False
        for receiver, response in signal_response:
            if response is False:
                # Se houver erro na otimização, desfaz a transação
                transaction.set_rollback(True)
                return Response(
                    {"error": "Não foi possível otimizar a rota. Verifique se todos os passageiros têm endereço principal cadastrado e se o veículo foi definido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Se chegou aqui, a otimização foi bem sucedida
        route.save()
        return Response(RouteReadSerializer(route).data, status=status.HTTP_201_CREATED)

    # Erro de validação
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
