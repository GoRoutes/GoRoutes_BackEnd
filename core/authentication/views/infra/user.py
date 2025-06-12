from rest_framework.viewsets import ModelViewSet
from core.authentication.models import User
from rest_framework.response import Response
from rest_framework import status
from core.authentication.serializers.infra import UserSerializer, CustomTokenObtainPairSerializer
from core.authentication.views.handlers.user_handlers import destroy_user
from rest_framework_simplejwt.views import TokenObtainPairView

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return destroy_user(request, pk)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get(self):
        return Response({"detail": "Insira suas credenciais"}, status=status.HTTP_200_OK)