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
                order=0  # Valor temporário
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
        
        # **ATUALIZAR A ORDEM DOS PASSAGEIROS APÓS A OTIMIZAÇÃO**
        if hasattr(route, 'coords_passageiros') and route.coords_passageiros:
            _atualizar_ordem_passageiros(route, passenger_list)
        
        route.save()
        return Response(RouteReadSerializer(route).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def _atualizar_ordem_passageiros(route, passenger_list):
    """
    Atualiza a ordem dos passageiros baseado na ordem do coords_passageiros
    """
    try:
        # Obter a ordem otimizada do addresses_order
        if route.addresses_order:
            caminho_otimizado = json.loads(route.addresses_order)
            
            # Remover origem e destino, ficando apenas com os endereços dos passageiros
            enderecos_passageiros = caminho_otimizado[1:-1] if len(caminho_otimizado) > 2 else []
            
            # Para cada endereço na ordem otimizada, encontrar o passageiro correspondente
            for order_index, endereco in enumerate(enderecos_passageiros):
                # Buscar o passageiro que tem este endereço
                for passenger_data in passenger_list:
                    if isinstance(passenger_data, int):
                        passenger_obj = Passenger.objects.get(pk=passenger_data)
                    else:
                        passenger_obj = passenger_data
                    
                    # Obter endereço principal do passageiro
                    main_address = passenger_obj.address.filter(is_main=True).first()
                    if main_address:
                        full_address = f"{main_address.street}, {main_address.number} - {main_address.neighborhood}, {main_address.city} - {main_address.state}"
                        
                        # Verificar se é o mesmo endereço (pode precisar de normalização)
                        if _enderecos_sao_iguais(full_address, endereco):
                            # Atualizar a ordem do PassengerRoute
                            passenger_route = PassengerRoute.objects.get(
                                passenger=passenger_obj, 
                                route=route
                            )
                            passenger_route.order = order_index
                            passenger_route.save()
                            break
        
        print(f"✅ Ordem dos passageiros atualizada com sucesso")
        
    except Exception as e:
        print(f"⚠️ Erro ao atualizar ordem dos passageiros: {e}")

def _enderecos_sao_iguais(endereco1, endereco2):
    """
    Compara se dois endereços são iguais (com tolerância)
    """
    import unicodedata
    
    # Normalizar endereços para comparação
    def normalizar(endereco):
        return ''.join(c for c in unicodedata.normalize('NFD', endereco.upper()) 
                      if unicodedata.category(c) != 'Mn').replace(' ', '')
    
    return normalizar(endereco1) in normalizar(endereco2) or normalizar(endereco2) in normalizar(endereco1)

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