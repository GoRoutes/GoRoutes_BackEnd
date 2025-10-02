from core.goroutes.models import Route, PassengerRoute
from core.authentication.models import Passenger
from core.goroutes.serializers import RouteWriteSerializer, RouteReadSerializer, RouteRetrieveSerializer
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

def retrieve_route(request, pk):
    """
    Retrieve a specific route by its primary key.
    """
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'detail': 'Rota não encontrada'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RouteRetrieveSerializer(route)
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
            driver=data.get("driver"),
            addresses_order=data.get("addresses_order", []),
            optimized_route_url=data.get("optimized_route_url", "")
        )

        # Criar PassengerRoute para cada passageiro mantendo a ordem
        passenger_list = data.get("passengers_list", [])
        
        # **MUDANÇA PRINCIPAL AQUI**: Usar a ordem do signal
        # Inicialmente criamos sem ordem, o signal vai otimizar e depois atualizamos
        for passenger in passenger_list:
            if isinstance(passenger, int):
                try:
                    passenger = Passenger.objects.get(pk=passenger)
                except Passenger.DoesNotExist:
                    continue

            # Cria inicialmente sem ordem (será definida depois do signal)
            PassengerRoute.objects.create(
                passenger=passenger, 
                route=route,
            )

        # Agora que os PassengerRoute foram criados, ativar auto_recalculate
        route.auto_recalculate = True
        
        # Chamar o signal manualmente para otimização
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
                transaction.set_rollback(True)
                return Response(
                    {"error": "Não foi possível otimizar a rota. Verifique se todos os passageiros têm endereço principal cadastrado e se o veículo foi definido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        route.save()
        return Response(RouteReadSerializer(route).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_latitude_longitude(address):
    """
    Get latitude and longitude from address using Google Maps API
    """
    from django.conf import settings
    import requests
    
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None
    except Exception as e:
        print(f"Error getting latitude and longitude: {e}")
        return None, None
    
def destroy_route(request, pk):
    """
    Delete a specific route and its associated passenger routes.
    """
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'detail': 'Rota não encontrada'}, status=status.HTTP_404_NOT_FOUND)

    try:
        with transaction.atomic():
            # Primeiro exclui todos os PassengerRoute associados
            PassengerRoute.objects.filter(route=route).delete()
            
            # Depois exclui a rota
            route.delete()
            
        return Response(
            {'detail': 'Rota e passageiros associados excluídos com sucesso'},
            status=status.HTTP_204_NO_CONTENT
        )
        
    except Exception as e:
        return Response(
            {'detail': f'Erro ao excluir rota: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )