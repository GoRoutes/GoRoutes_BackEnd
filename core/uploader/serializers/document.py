from rest_framework import serializers
from core.uploader.models import Document
from django.conf import settings

class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    description = serializers.CharField(max_length=255, required=False)
    file_download = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "file", "description", "uploaded_on", "folder", "attachment_key", "public_id", "file_download"]

    def get_file_download(self, obj):
        """
        Gera a URL de download do arquivo com base no public_id.
        """
        return f"https://res.cloudinary.com/{settings.CLOUD_NAME}/raw/upload/{obj.public_id}"

    def validate_file(self, value):
        """
        Valida o tipo de arquivo do documento.
        Aceita apenas alguns tipos de documentos (PDF, DOC, DOCX, XLS, XLSX, TXT, ZIP).
        """
        allowed_types = [
            'application/pdf',
            'application/msword',  
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'application/zip',
        ]

        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF, DOC, DOCX, XLS, XLSX, TXT and ZIP files are allowed."
            )
        return value
