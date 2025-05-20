from rest_framework.viewsets import ModelViewSet
from core.authentication.models import User

from core.authentication.serializers.infra import UserSerializer
from core.authentication.views.handlers.user_handlers import destroy_user

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return destroy_user(request, pk)
