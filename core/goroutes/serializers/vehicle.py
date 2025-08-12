from rest_framework import serializers
from core.goroutes.models import Vehicle
from core.uploader.utils.create_image import create_image

class VehicleSerializer(serializers.ModelSerializer):
    picture_file = serializers.ImageField(write_only=True, required=False, allow_null=True)
    picture = serializers.SerializerMethodField()  # <- aqui

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'plate',
            'model',
            'seats',
            'status',
            'picture',
            'picture_file'
        ]

    def create(self, validated_data):
        picture_file = validated_data.pop("picture_file", None)
        
        if picture_file:
            image = create_image(
                file=picture_file,
                description=f"Foto do veículo {validated_data.get('model', '')}",
                folder_path="vehicles"
            )
            validated_data["picture"] = image

        return super().create(validated_data)

    def get_picture(self, obj):
        # Aqui pega a URL da imagem
        if obj.picture and hasattr(obj.picture, 'file') and obj.picture.file:
            # Supondo que obj.picture.file seja a URL (string) da imagem no seu modelo Image
            return str(obj.picture.file)
        return None
