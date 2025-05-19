from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from core.authentication.models import User
from django.conf import settings
from passageidentity import Passage, PassageError
from rest_framework.exceptions import AuthenticationFailed

from core.authentication.serializers import UserSerializer

PASSAGE_APP_ID = settings.PASSAGE_APP_ID
PASSAGE_API_KEY = settings.PASSAGE_API_KEY
PASSAGE_AUTH_STRATEGY = settings.PASSAGE_AUTH_STRATEGY
psg = Passage(PASSAGE_APP_ID, PASSAGE_API_KEY)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        try:
            user = User.objects.get(id=user_id)

            if user.passage_id:
                try:
                    psg.deleteUser(user.passage_id)
                except PassageError as e:
                    # Log the error, but proceed to delete the local user
                    print(f"Passage deletion error: {str(e)}")
        
            # Delete the user locally regardless of Passage errors
            user.delete()
            return Response({"detail": "User deleted successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
