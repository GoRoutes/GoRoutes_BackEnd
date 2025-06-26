from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from core.authentication.models import User
from core.uploader.models import Image  
from core.uploader.utils.create_image import create_image

class UpdatePicture(APIView):
    """
    View to handle updating a user's profile picture.
    """

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Use POST to update your profile picture."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_id = int(request.data["user_id"])
        new_picture = request.FILES.get("picture")

        user = User.objects.filter(id=user_id).first()

        image_created = create_image(
            file=new_picture,
            folder_path="profiles",
            description="Profile picture for user {}".format(user_id)
        )

        user.picture = image_created
        user.save()

        return Response({"detail": "Profile picture updated successfully.",
                         "picture": image_created.file}, status=status.HTTP_200_OK)