import googlemaps
from .save_distance_cache import salvar_distancia_no_cache

def calcular_distancia_api(api_key: str, obter_coordenadas_do_cache_func, origem: str, destino: str):
    """
    Calcula distância usando Google Distance Matrix API como fallback
    """
    try:
        if not api_key:
            print(f"❌ API Key não configurada para fallback")
            return None
        
        print(f"📍 Calculando via API: {origem} -> {destino}")
        
        gmaps = googlemaps.Client(key=api_key)
        
        matrix_result = gmaps.distance_matrix(
            origins=[origem],
            destinations=[destino],
            mode="driving",
            language="pt-BR",
            units="metric"
        )
        
        if matrix_result['status'] == 'OK':
            element = matrix_result['rows'][0]['elements'][0]
            
            if element['status'] == 'OK':
                distance = element['distance']['value']  
                duration = element['duration']['value']  
                
                print(f"✅ API retornou: {distance}m, {duration}s")
                
                salvar_distancia_no_cache(obter_coordenadas_do_cache_func, origem, destino, distance, duration)
                
                return {
                    'distance': distance,
                    'duration': duration
                }
            else:
                print(f"❌ API não conseguiu calcular rota: {element['status']}")
                return None
        else:
            print(f"❌ Erro na API: {matrix_result['status']}")
            return None
            
    except Exception as e:
        print(f"🚨 Erro na API Distance Matrix: {e}")
        return None