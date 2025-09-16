import requests
import time
import logging

def verificar_enderecos(enderecos, api_key: str):
    """
    Verifica se os endereços existem utilizando a API de Geocodificação do Google Maps.

    Args:
        enderecos: Lista de endereços a serem verificados.
        api_key: Chave da API do Google Maps.

    Returns:
        Dicionário com endereços válidos e inválidos.
    """
    enderecos_invalidos = []
    enderecos_validos = {}

    for endereco in enderecos:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': endereco,
                'key': api_key
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data['status'] != 'OK' or not data.get('results'):
                enderecos_invalidos.append(endereco)
                enderecos_validos[endereco] = False
            else:
                enderecos_validos[endereco] = True

            time.sleep(0.1)  # Respeitar limites da API
        except Exception as e:
            raise Exception(f"Erro ao verificar endereço {endereco}: {str(e)}")

    if enderecos_invalidos:
        raise ValueError(f"Os seguintes endereços são inválidos: {', '.join(enderecos_invalidos)}")

    return enderecos_validos
