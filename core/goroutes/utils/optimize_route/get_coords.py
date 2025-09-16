import requests
import logging

def obter_coordenadas(endereco: str, api_key: str):
    """
    Obtém as coordenadas (latitude, longitude) de um endereço.

    Args:
        endereco: Endereço em formato string.
        api_key: Chave da API do Google Maps.

    Returns:
        Lista [latitude, longitude]
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': endereco, 'key': api_key}
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return [location['lat'], location['lng']]
        else:
            raise ValueError(f"Endereço inválido: {endereco}")
    except Exception as e:
        logging.error(f"Erro ao obter coordenadas: {str(e)}")
        raise
