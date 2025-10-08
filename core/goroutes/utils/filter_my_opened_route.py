from rest_framework.views import APIView
from rest_framework.response import Response
from core.goroutes.models import DailyRoute
from core.goroutes.serializers.infra import DailyRouteListSerializer
from core.authentication.models import Passenger

class FilterMyOpenedPassengerRoute(APIView):
    def get(self, request, passenger_id):
        try:
            # Verifica se o passageiro existe
            passenger = Passenger.objects.filter(id=passenger_id).first()
            if not passenger:
                return Response({
                    "has_route": False,
                    "route": None
                })
            
            # Filtra as rotas do passageiro
            passenger_routes = DailyRoute.objects.filter(
                presences__passenger_route_id=passenger_id,
                is_active=True
            )
            
            route = passenger_routes.first()
            
            if route:
                route_data = DailyRouteListSerializer(route).data
                return Response({
                    "has_route": True,
                    "route": route_data
                })
            else:
                return Response({
                    "has_route": False,
                    "route": None
                })
                
        except Exception as e:
            return Response({
                "has_route": False,
                "route": None,
                "error": "Erro ao buscar rota do passageiro."
            }, status=500)