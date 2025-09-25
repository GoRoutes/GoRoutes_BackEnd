from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.goroutes.models.daily_route import DailyRoute

class CheckActiveDailyRouteDriverView(APIView):
    """
    Verifica se existe alguma DailyRoute de um motorista específico que ainda não foi finalizada (finalized=False)
    """

    def get(self, request, driver_id, *args, **kwargs):
        has_active_route = DailyRoute.objects.filter(driver_id=driver_id, finalized=False).exists()

        return Response(
            {
                "driver_id": driver_id,
                "has_active_route": has_active_route,
                "message": "Tem rota ativa ainda" if has_active_route else "Nenhuma rota ativa"
            },
            status=status.HTTP_200_OK
        )
