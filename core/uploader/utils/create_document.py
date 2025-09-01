import uuid
from cloudinary.uploader import upload
from core.uploader.models import Document

def create_document(file, description="", folder_path=""):
    """
    Função para cadastrar um documento no modelo Document.
    
    Args:
        file: Arquivo do documento (ex.: InMemoryUploadedFile).
        description: (Opcional) Uma descrição para o documento.
        folder_path: (Opcional) Pasta no Cloudinary para armazenar o arquivo.
    
    Returns:
        document: Instância do modelo Document criada.
    """
    try:
        cloudinary_response = upload(file, folder=folder_path, resource_type="raw")
        
        document = Document.objects.create(
            attachment_key=uuid.uuid4(),
            public_id=cloudinary_response['public_id'],
            file=cloudinary_response['secure_url'],
            description=description,
            folder=folder_path
        )
        return document
    except Exception as e:
        raise Exception(f"Erro ao criar o documento: {str(e)}")
