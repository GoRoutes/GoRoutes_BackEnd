from rest_framework import viewsets, status
from rest_framework.response import Response
from cloudinary.uploader import upload
from core.uploader.models import Image
import uuid
from core.uploader.serializers import ImageUploadSerializer
from config import settings

class ImagesViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            description = serializer.validated_data.get('description', '')
            folder = serializer.validated_data.get('folder', 'media/images')

            cloudinary_response = upload(file, folder="media/" + folder)

            # URL original
            original_url = cloudinary_response['secure_url']
            public_id = cloudinary_response['public_id']

            # Criar URL da versão redonda usando transformação do Cloudinary
            # Exemplo: cortar como um círculo de 200x200 pixels
            # https://res.cloudinary.com/your_cloud_name/image/upload/c_thumb,g_face,r_max,w_200,h_200/public_id.jpg
            # Atenção: substitua 'your_cloud_name' pelo seu cloud_name do Cloudinary

            file_rounded_url = f"https://res.cloudinary.com/{settings.CLOUD_NAME}/image/upload/c_thumb,g_face,r_max,w_200,h_200/{public_id}.jpg"

            image = Image.objects.create(
                attachment_key=uuid.uuid4(),
                public_id=public_id,
                file=original_url,
                file_rounded=file_rounded_url,
                folder=folder,
                description=description
            )

            return Response({
                'id': image.id,
                'attachment_key': image.attachment_key,
                'public_id': image.public_id,
                'file': image.file,
                'file_rounded': image.file_rounded,
                'description': image.description,
                'uploaded_on': image.uploaded_on,
                'folder': image.folder
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
