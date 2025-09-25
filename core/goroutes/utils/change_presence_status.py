from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.goroutes.models.daily_route import Presence


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
