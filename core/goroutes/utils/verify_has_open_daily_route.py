from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.goroutes.models.daily_route import DailyRoute
from core.goroutes.serializers import DailyRouteListSerializer

class CheckActiveDailyRouteDriverView(APIView):
    """
    Verifica se existe alguma DailyRoute de um motorista específico que ainda não foi finalizada (finalized=False)
    e retorna a rota ativa completa.
    """

    def get(self, request, driver_id, *args, **kwargs):
        active_route = DailyRoute.objects.filter(driver_id=driver_id, finalized=False).first()
        has_active_route = active_route is not None

        serialized_route = DailyRouteListSerializer(active_route).data if has_active_route else None

        return Response(
            {
                "driver_id": driver_id,
                "has_active_route": has_active_route,
                "message": "Tem rota ativa ainda" if has_active_route else "Nenhuma rota ativa",
                "active_route": serialized_route
            },
            status=status.HTTP_200_OK
        )
