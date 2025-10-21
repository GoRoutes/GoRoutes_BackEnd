from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from  core.authentication.models import Driver
from core.uploader.utils.create_document import create_document

class UpdateDocumentDriver(APIView):
    """
    View to handle updating a driver's documents.
    """

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Use POST to update your driver's documents."}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        document_type = request.data["document_type"]
        driver_id = int(request.data["driver_id"])
        new_document = request.FILES.get("document")

        driver = Driver.objects.filter(id=driver_id).first()

        document_created = create_document(
            file=new_document,
            folder_path="documents",
            description="Driver document for driver {}".format(document_type)
        )

        if(document_type == "cnh_document"):
            driver.cnh_document = document_created
            driver.save()
        elif(document_type == "course_document"):
            driver.course_document = document_created
            driver.save()
        elif(document_type == "toxic_exam_document"):
            driver.toxic_exam_document = document_created
            driver.save()

        return Response({"detail": "Profile document updated successfully.",
                         "document": document_created.file}, status=status.HTTP_200_OK)