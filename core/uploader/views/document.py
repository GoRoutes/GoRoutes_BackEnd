from rest_framework import viewsets, status
from rest_framework.response import Response
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from core.uploader.models import Document
import uuid
from core.uploader.serializers import DocumentUploadSerializer
import requests
from django.http import HttpResponse
from django.views import View
from config import settings


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            description = serializer.validated_data.get('description', '')
            folder = serializer.validated_data.get('folder', 'documents')
            folder = folder.lstrip('/')

            try:
                cloudinary_response = upload(
                    file,
                    folder=folder,
                    resource_type="raw"
                )

                public_id = cloudinary_response['public_id']

                file_url_view, _ = cloudinary_url(
                    public_id,
                    resource_type="raw",
                    secure=True,
                    attachment=False  
                )

                file_url_download, _ = cloudinary_url(
                    public_id,
                    resource_type="raw",
                    secure=True,
                    attachment=True  
                )

                document = Document.objects.create(
                    attachment_key=uuid.uuid4(),
                    public_id=public_id,
                    file=file_url_view,  
                    folder=folder,
                    description=description
                )

                return Response({
                    'id': document.id,
                    'attachment_key': document.attachment_key,
                    'public_id': document.public_id,
                    'file_view': file_url_view,        
                    'file_download': file_url_download, 
                    'description': document.description,
                    'uploaded_on': document.uploaded_on,
                    'folder': document.folder
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {"detail": f"Erro ao criar o documento: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DownloadDocumentView(View):
    """
    View para baixar um documento/foto do Cloudinary usando o public_id.
    """

    def get(self, request, public_id):
        try:
            url = f"https://res.cloudinary.com/{settings.CLOUD_NAME}/raw/upload/{public_id}"

            response = requests.get(url, stream=True)

            if response.status_code == 200:
                filename = public_id.split("/")[-1]

                content_type = response.headers.get("Content-Type", "application/octet-stream")

                resp = HttpResponse(response.content, content_type=content_type)
                resp["Content-Disposition"] = f'attachment; filename="{filename}"'
                return resp
            else:
                return HttpResponse("Arquivo não encontrado no Cloudinary.", status=404)

        except Exception as e:
            return HttpResponse(f"Erro ao baixar o arquivo: {str(e)}", status=500)
