try:
    from core.goroutes.models import DataCacheRoute
except ImportError:
    pass

def salvar_distancia_no_cache(obter_coordenadas_do_cache_func, origem: str, destino: str, distance: int, duration: int):
    """
    Salva distância calculada no DataCacheRoute para futuras consultas
    """
    try:
        # Obtém coordenadas para salvar também
        coord_origem = obter_coordenadas_do_cache_func(origem, usar_api_fallback=True)
        coord_destino = obter_coordenadas_do_cache_func(destino, usar_api_fallback=True)
        
        if coord_origem and coord_destino:
            lat_origem, lng_origem = coord_origem
            lat_destino, lng_destino = coord_destino
            
            # Salva no DataCacheRoute
            DataCacheRoute.objects.update_or_create(
                origin=origem,
                destination=destino,
                defaults={
                    'distance': distance,
                    'duration': duration,
                    'latitude_origin': str(lat_origem),
                    'longitude_origin': str(lng_origem),
                    'latitude_destination': str(lat_destino),
                    'longitude_destination': str(lng_destino),
                    'polyline': ""
                }
            )
            
            print(f"💾 Distância salva no cache: {origem} -> {destino}")
        else:
            print(f"⚠️ Não foi possível salvar no cache - coordenadas não encontradas")
            
    except Exception as e:
        print(f"⚠️ Erro ao salvar distância no cache: {e}")