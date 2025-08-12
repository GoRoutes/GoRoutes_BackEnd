from rest_framework import serializers
from core.uploader.models import Image

class ImageUploadSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(required=True)
    file_rounded = serializers.CharField(read_only=True)
    description = serializers.URLField(max_length=255, required=False)

    class Meta:
        model = Image
        fields = ["id", "file", "description", "uploaded_on", "folder", "file_rounded"]

    def validate_file(self, value):
        """
        Valida o tipo de arquivo da imagem.
        Aceita apenas arquivos de imagem.
        """
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Only JPEG and PNG images are allowed.")
        return value
