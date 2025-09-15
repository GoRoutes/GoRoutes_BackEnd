from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from core.goroutes.models import Vehicle
from core.uploader.utils.create_image import create_image


class UpdatePictureVehicle(APIView):
    """
    View to handle updating a vehicle's picture.
    """

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Use POST to update your vehicle picture."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        vehicle_id = int(request.data["vehicle_id"])
        new_picture = request.FILES.get("picture")

        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

        image_created = create_image(
            file=new_picture,
            folder_path="vehicles",
            description="Vehicle picture for vehicle {}".format(vehicle_id)
        )

        vehicle.picture = image_created
        vehicle.save()

        return Response({"detail": "Vehicle picture updated successfully.",
                         "picture": image_created.file}, status=status.HTTP_200_OK)


