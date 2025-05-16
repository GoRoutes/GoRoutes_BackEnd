from rest_framework import viewsets

from core.authentication.models import User
from core.authentication.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'delete']
