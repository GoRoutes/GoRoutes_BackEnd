from core.goroutes.models import DailyRoute, PassengerRoute
from core.authentication.models import Passenger
from core.goroutes.serializers import DailyRouteWriteSerializer, DailyRouteListSerializer, DailyRouteRetrieveSerializer
from core.goroutes.serializers.handlers import get_data_of_route
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from core.goroutes.utils.optimize_route import obter_coordenadas
from core.goroutes.utils.optimize_route.directions import fetch_directions

def list_dailyroutes(request):
    """
    Função externa para listar todas as rotas diárias.
    """
    daily_routes = DailyRoute.objects.all().order_by('date', 'init_hour')
    serializer = DailyRouteListSerializer(daily_routes, many=True)
    return Response(serializer.data)

def retrieve_dailyroute(request, pk):
    """
    Função externa para recuperar uma rota diária específica.
    """
    try:
        daily_route = DailyRoute.objects.get(pk=pk)
    except DailyRoute.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DailyRouteRetrieveSerializer(daily_route)
    return Response(serializer.data)

from rest_framework.response import Response
from rest_framework import status
from core.goroutes.serializers import DailyRouteWriteSerializer, DailyRouteListSerializer
from core.goroutes.models import DailyRoute, Presence
from django.db import transaction

def create_dailyroute(request):
    serializer = DailyRouteWriteSerializer(data=request.data)

    if serializer.is_valid():
        route_obj = serializer.validated_data["route"]
        data = serializer.prepare_route_of_father_route(route_obj)
        passengers_list_bruto = serializer.validated_data.get("passengers_list", [])
        passengers_list = [p.id for p in passengers_list_bruto]

        if not passengers_list:
            raw_alias = request.data.get("passenger_list")
            if isinstance(raw_alias, list):
                try:
                    passengers_list = [int(pid) for pid in raw_alias]
                except Exception:
                    passengers_list = []
        original = serializer.validated_data.get("original", True)

        try:
            with transaction.atomic():
                
                vehicle = data.get("vehicle")
                driver = data.get("driver")

                if original:
                    daily_route_obj = DailyRoute.objects.create(
                        name=data["name"],
                        origin=data["origin"],
                        route=route_obj,
                        destination=data["destination"],
                        init_hour=data["init_hour"],
                        end_hour=data["end_hour"],
                        latitude_origin=data["latitude_origin"],
                        longitude_origin=data["longitude_origin"],
                        latitude_destination=data["latitude_destination"],
                        longitude_destination=data["longitude_destination"],
                        vehicle_id=vehicle["id"] if isinstance(vehicle, dict) else vehicle,
                        driver_id=driver["id"] if isinstance(driver, dict) else driver,
                        auto_recalculate=data.get("auto_recalculate", True),
                        is_active=True,
                        date=request.data.get("date"),
                        optimized_route_url=data.get("optimized_route_url"),
                        overview_polyline=data.get("overview_polyline"),
                        original=True
                    )
                else:

                    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
                    if not api_key:
                        raise ValueError("API key do Google Maps não encontrada")

                    if not passengers_list:
                        raise ValueError("Nenhum passageiro informado (use passengers_list ou passenger_list)")


                    formatted_addresses = []
                    for passenger_id in passengers_list:
                        passenger_instance = Passenger.objects.get(id=passenger_id)
                        main_address = passenger_instance.address.filter(is_main=True).first()
                        if main_address:
                            full_address = f"{main_address.street}, {main_address.number} - {main_address.neighborhood}, {main_address.city} - {main_address.state}"
                            formatted_addresses.append(full_address)

                    if not formatted_addresses:
                        raise ValueError("Passageiros informados não possuem endereço principal")

                    coords_passageiros = []
                    for addr in formatted_addresses:
                        lat, lng = obter_coordenadas(addr, api_key)
                        coords_passageiros.append([lat, lng])

                    directions = fetch_directions(
                        origin=data["origin"],
                        destination=data["destination"],
                        waypoints=formatted_addresses,
                        api_key=api_key,
                    )

                    daily_route_obj = DailyRoute.objects.create(
                        name=data["name"],
                        origin=data["origin"],
                        route=route_obj,
                        destination=data["destination"],
                        init_hour=data["init_hour"],
                        end_hour=data["end_hour"],
                        latitude_origin=data["latitude_origin"],
                        longitude_origin=data["longitude_origin"],
                        latitude_destination=data["latitude_destination"],
                        longitude_destination=data["longitude_destination"],
                        vehicle_id=vehicle["id"] if isinstance(vehicle, dict) else vehicle,
                        driver_id=driver["id"] if isinstance(driver, dict) else driver,
                        auto_recalculate=data.get("auto_recalculate", True),
                        is_active=True,
                        date=request.data.get("date"),
                        original=False,
                        coords_passageiros=coords_passageiros,
                        points=directions.get("points", []),
                        overview_polyline=directions.get("overview_polyline", {}),
                        addresses=directions.get("ordered_addresses", formatted_addresses),
                        optimized_route_url=directions.get("link_maps"),
                    )

                if original:
                    passenger_routes = PassengerRoute.objects.filter(route=route_obj)
                    for pr in passenger_routes:
                        Presence.objects.create(
                            daily_route=daily_route_obj,
                            passenger_route=pr.passenger,  # continua salvando Passenger na Presence
                            present=False
                        )
                else:
                    for passenger_id in passengers_list:
                        passenger_instance = Passenger.objects.get(id=passenger_id)
                        Presence.objects.create(
                            daily_route=daily_route_obj,
                            passenger_route=passenger_instance,
                            present=False
                        )

            # Retorna os dados da DailyRoute já com presenças
            result_serializer = DailyRouteListSerializer(daily_route_obj)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
