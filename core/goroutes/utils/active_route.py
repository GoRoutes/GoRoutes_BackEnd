# core/goroutes/utils.py
from rest_framework.views import APIView
from rest_framework.response import Response
from core.goroutes.models import Route

class ActivateRouteView(APIView):
    def post(self, request):
        route_id = request.data.get('id')

        if not route_id:
            return Response({"error": "ID da rota não fornecido"}, status=400)

        route_selected = Route.objects.filter(id=route_id).first()

        if route_selected:
            route_selected.is_active = not (route_selected.is_active)
            route_selected.save()
            return Response({
                "message": "Rota atualizada com sucesso",
                "route": {
                    "id": route_selected.id,
                    "is_active": route_selected.is_active
                }
            })
        else:
            return Response({"error": "Rota não encontrada"}, status=404)
