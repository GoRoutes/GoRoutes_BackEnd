from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
import re
import googlemaps
from django.conf import settings
from core.goroutes.models.daily_route import Presence
from core.goroutes.utils import otimizar_rotas_vans


class ChangePresenceStatusView(APIView):
    """
    API endpoint para alterar o status de uma presença.
    """

    def post(self, request, *args, **kwargs):
        data = request.data

        # valida campos obrigatórios
        required_fields = ["daily_route", "passenger_route", "new_status"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Campo obrigatório ausente: {field}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # busca presence pelo daily_route e passenger_route
            presence = Presence.objects.filter(
                daily_route_id=data["daily_route"],
                passenger_route_id=data["passenger_route"],
            ).first()

            if not presence:
                return Response(
                    {"error": "Presence não encontrada para o daily_route e passenger_route fornecidos."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # valida status
            if data["new_status"] not in dict(Presence.Status.choices):
                return Response(
                    {
                        "error": f"Status inválido '{data['new_status']}'. "
                                 f"Opções válidas: {list(dict(Presence.Status.choices).keys())}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # atualiza
            presence.status = data["new_status"]
            presence.save()

            # Recalcular rota a partir do passageiro marcado até o destino
            daily_route = presence.daily_route

            # Origem = endereço do passageiro marcado (principal)
            passenger = presence.passenger_route
            main_address = passenger.address.filter(is_main=True).first()
            if not main_address:
                return Response({"error": "Passageiro não possui endereço principal."}, status=status.HTTP_400_BAD_REQUEST)

            origin_from_passenger = f"{main_address.street}, {main_address.number} - {main_address.neighborhood}, {main_address.city} - {main_address.state}"

            # Waypoints = outros passageiros ainda pendentes (exclui o atual)
            pending_presences = daily_route.presences.exclude(passenger_route=passenger).filter(status__in=[
                Presence.Status.NAO_PEGO, Presence.Status.PRESENTE
            ])

            addresses = []
            for p in pending_presences:
                other_passenger = p.passenger_route
                other_main = other_passenger.address.filter(is_main=True).first()
                if other_main:
                    addresses.append({
                        "local": f"{other_main.street}, {other_main.number} - {other_main.neighborhood}, {other_main.city} - {other_main.state}",
                        "passageiros": 1
                    })

            # Vans (formato esperado)
            if daily_route.vehicle is None:
                return Response({"error": "DailyRoute sem veículo."}, status=status.HTTP_400_BAD_REQUEST)

            vans = [{
                "van": daily_route.vehicle.id,
                "lugares": daily_route.vehicle.seats,
                "endereco_inicial": origin_from_passenger
            }]

            endereco_final = daily_route.destination
            api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
            if not api_key:
                return Response({"error": "GOOGLE_MAPS_API_KEY não configurada."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            rotas = otimizar_rotas_vans(addresses, endereco_final, vans, api_key)

            # Opcional: atualizar alguns campos do daily_route caso tenhamos retorno
            if rotas:
                rota = rotas[0]
                daily_route.optimized_route_url = rota.get('link_maps')
                daily_route.coords_passageiros = rota.get('coords_passageiros', [])

                # Buscar dados detalhados da rota via API Google Maps
                try:
                    gmaps = googlemaps.Client(key=api_key)
                    
                    # Usar o caminho otimizado para obter dados completos da rota
                    waypoints = rota['caminho'][1:-1]  # Remove início e fim (já incluídos no origin/destination)
                    
                    directions_result = gmaps.directions(
                        origin=rota['caminho'][0],  # Endereço inicial
                        destination=rota['caminho'][-1],  # Endereço final
                        waypoints=waypoints,
                        mode="driving",
                        optimize_waypoints=False,  # Já estão otimizados pelo nosso algoritmo
                        language="pt-BR"
                    )
                    
                    if directions_result:
                        rota_detalhada = directions_result[0]
                        
                        # overview_polyline
                        daily_route.overview_polyline = rota_detalhada.get('overview_polyline', {})
                        
                        # Extrair steps e gerar markers + points
                        steps = []
                        points = []

                        for leg in rota_detalhada.get('legs', []):
                            for step in leg.get('steps', []):
                                clean_instruction = re.sub(r'<[^>]+>', '', step.get('html_instructions', ''))
                                steps.append({
                                    "distance": step.get("distance", {}),
                                    "duration": step.get("duration", {}),
                                    "start_location": step.get("start_location", {}),
                                    "end_location": step.get("end_location", {}),
                                    "polyline": step.get("polyline", {}),
                                    "html_instructions": clean_instruction
                                })

                                polyline_points = step.get("polyline", {}).get("points")
                                if polyline_points:
                                    points.append(polyline_points)

                        daily_route.markers = steps
                        daily_route.points = points
                        
                        print(f"Dados detalhados da rota obtidos com sucesso: {len(steps)} steps")
                    else:
                        print("Não foi possível obter dados detalhados da rota da API")
                        # Fallback: usar dados básicos da otimização
                        daily_route.overview_polyline = {}
                        daily_route.markers = []
                        daily_route.points = []

                except Exception as e:
                    print(f"Erro ao obter dados detalhados da rota: {e}")
                    # Fallback em caso de erro
                    daily_route.overview_polyline = {}
                    daily_route.markers = []
                    daily_route.points = []

                daily_route.save(update_fields=[
                    "optimized_route_url",
                    "coords_passageiros",
                    "overview_polyline",
                    "markers",
                    "points",
                ]) 
                

            # valida status
            return Response(
                {
                    "message": "Status atualizado com sucesso.",
                    "presence": {
                        "id": presence.id,
                        "daily_route": presence.daily_route.id,
                        "passenger_route": presence.passenger_route.id,
                        "status": presence.status,
                    }
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )