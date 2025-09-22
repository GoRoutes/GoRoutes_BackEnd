from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import signals

from core.goroutes.models import Route
from core.goroutes.serializers import RouteRetrieveSerializer


class RecalculateRoute(APIView):
    """
    Recalcula uma rota existente reaproveitando a lógica do signal de otimização.
    """

    def post(self, request, *args, **kwargs):
        route_id = request.data.get("id")
        if not route_id:
            return Response({"error": "ID da rota não fornecido"}, status=status.HTTP_400_BAD_REQUEST)

        route = Route.objects.filter(id=route_id).first()
        if not route:
            return Response({"error": "Rota não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Habilita recálculo e dispara o pre_save manualmente para validar/otimizar
        route.auto_recalculate = True

        signal_response = signals.pre_save.send(
            sender=Route,
            instance=route,
            raw=False,
            using='default',
            update_fields=None
        )

        for _, response in signal_response:
            if response is False:
                return Response(
                    {"error": "Não foi possível recalcular a rota. Verifique se todos os passageiros têm endereço principal cadastrado, se o veículo está definido e a API key do Google está configurada."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        route.save()
        return Response(RouteRetrieveSerializer(route).data, status=status.HTTP_200_OK)


