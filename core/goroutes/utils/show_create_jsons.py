import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
JSON_FILE_PATH = os.path.join(BASE_DIR, "json_objects_create.json") 


class LocalJsonView(APIView):
    """
    Lê um JSON local e retorna os dados formatados no estilo API root do DRF.
    """

    def get(self, request, *args, **kwargs):
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            # transforma o JSON em um dicionário de endpoints, caso seja um array de objetos
            # aqui assumimos que cada item do JSON tem "name" e "url"
            if isinstance(data, list):
                api_root = {item.get("name", f"item_{i}"): item.get("url", "") for i, item in enumerate(data)}
            elif isinstance(data, dict):
                api_root = data
            else:
                api_root = {"data": data}

            return Response(api_root, status=status.HTTP_200_OK)

        except FileNotFoundError:
            return Response(
                {"error": "Arquivo JSON não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "O arquivo não contém um JSON válido."},
                status=status.HTTP_400_BAD_REQUEST
            )
