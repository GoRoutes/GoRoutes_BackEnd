from rest_framework import viewsets, status
from rest_framework.response import Response
from cloudinary.uploader import upload
from core.uploader.models import Image
import uuid
from core.uploader.serializers import ImageUploadSerializer

class ImagesViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método de criação para fazer o upload da imagem para o Cloudinary.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            description = serializer.validated_data.get('description', '')
            folder = serializer.validated_data.get('folder', 'media/images')

            cloudinary_response = upload(file, folder="media/" + folder)

            image = Image.objects.create(
                attachment_key=uuid.uuid4(),
                public_id=cloudinary_response['public_id'],
                file=cloudinary_response['secure_url'],
                folder=folder,
                description=description
            )

            return Response({
                'id': image.id,
                'attachment_key': image.attachment_key,
                'public_id': image.public_id,
                'file': image.file,
                'description': image.description,
                'uploaded_on': image.uploaded_on,
                'folder': image.folder
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)