from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
import re
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

                # Carregar JSON salvo e extrair overview_polyline, markers e points
                try:
                    json_path = os.path.join(settings.BASE_DIR, f"data_van_{daily_route.vehicle.id}.json")
                    with open(json_path, 'r', encoding='utf-8') as f:
                        rota_json = json.load(f)

                    daily_route.overview_polyline = rota_json['routes'][0].get('overview_polyline', {})

                    steps = []
                    points = []
                    for leg in rota_json['routes'][0].get('legs', []):
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
                except Exception:
                    # Em caso de falha na leitura/parse, ainda salvamos os campos básicos acima
                    pass

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
