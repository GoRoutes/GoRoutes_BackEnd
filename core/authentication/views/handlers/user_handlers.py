from rest_framework.response import Response
from core.authentication.models import User

def destroy_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"detail": "User deleted successfully"}, status=200)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)
