from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from  core.goroutes.models import Vehicle
from core.uploader.utils.create_document import create_document

class UpdateDocumentVehicle(APIView):
    """
    View to handle updating a vehicle's documents.
    """

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Use POST to update your vehicle's documents."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        document_type = request.data["document_type"]
        vehicle_id = int(request.data["vehicle_id"])
        new_document = request.FILES.get("document")

        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

        document_created = create_document(
            file=new_document,
            folder_path="profiles",
            description="Profile document for user {}".format(document_type)
        )

        if(document_type == "CRLV"):
            vehicle.CRLV = document_created
            vehicle.save()
        elif(document_type == "CV"):
            vehicle.CV = document_created
            vehicle.save()
        elif(document_type == "AD"):
            vehicle.AD = document_created
            vehicle.save()

        return Response({"detail": "Profile document updated successfully.",
                         "document": document_created.file}, status=status.HTTP_200_OK)