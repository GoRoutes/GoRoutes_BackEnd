import uuid
from cloudinary.uploader import upload
from core.uploader.models import Image

def create_image(file, description="", folder_path=""):
    """
    Função para cadastrar uma imagem no modelo Image.
    
    Args:
        file: Arquivo da imagem (ex.: InMemoryUploadedFile).
        description: (Opcional) Uma descrição para a imagem.
    
    Returns:
        image: Instância do modelo Image criada.
    """
    try:
        cloudinary_response = upload(file, folder=folder_path)
        
        image = Image.objects.create(
            attachment_key=uuid.uuid4(),
            public_id=cloudinary_response['public_id'],
            file=cloudinary_response['secure_url'],
            description=description,
            folder=folder_path
        )
        return image
    except Exception as e:
        raise Exception(f"Erro ao criar a imagem: {str(e)}")
