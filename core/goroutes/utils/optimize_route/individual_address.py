import requests

def verificar_endereco_individual(endereco: str, api_key: str):
    """
    Verifica um único endereço e retorna informações detalhadas.

    Args:
        endereco: Endereço em formato string.
        api_key: Chave da API do Google Maps.

    Returns:
        Dicionário com informações do endereço.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': endereco,
        'region': 'br',
        'language': 'pt-BR',
        'key': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        result = data['results'][0]
        return {
            'valido': True,
            'endereco_formatado': result['formatted_address'],
            'lat': result['geometry']['location']['lat'],
            'lng': result['geometry']['location']['lng']
        }
    else:
        return {
            'valido': False,
            'status': data['status'],
            'mensagem': data.get('error_message', 'Endereço não encontrado')
        }
