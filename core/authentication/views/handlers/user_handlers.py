from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from core.authentication.models import User

def destroy_user(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"detail": "User deleted successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)