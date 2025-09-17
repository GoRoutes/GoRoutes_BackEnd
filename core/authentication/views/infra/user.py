from pyparsing import C
from rest_framework.viewsets import ModelViewSet
from core.authentication.models import User
from rest_framework.response import Response
from rest_framework import status
from core.authentication.serializers.infra import UserListSerializer, CustomTokenObtainPairSerializer, UserRetrieveSerializer
from core.authentication.views.handlers.user_handlers import destroy_user
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from core.authentication.filters import  CombinedUserFilter

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CombinedUserFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserRetrieveSerializer
        return UserListSerializer

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return destroy_user(request, pk)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Insira suas credenciais"}, status=status.HTTP_200_OK)