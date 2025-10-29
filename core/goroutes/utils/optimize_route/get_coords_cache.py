from django.db import models
from .normalize_text import normalizar_texto
from .make_geocoding import fazer_geocoding_api

try:
    from core.goroutes.models import DataCacheRoute
    from core.authentication.models import Address
except ImportError:
    pass

def obter_coordenadas_do_cache(api_key: str, endereco: str, usar_api_fallback=True):
    """
    Busca coordenadas - com tratamento de acentos
    """
    try:
        print(f"🔍 Buscando coordenadas para: {endereco}")
        
        endereco_normalizado = normalizar_texto(endereco)
        
        cache_entries = DataCacheRoute.objects.filter(
            models.Q(origin__icontains=endereco) |
            models.Q(destination__icontains=endereco) |
            models.Q(origin__icontains=endereco_normalizado) |
            models.Q(destination__icontains=endereco_normalizado)
        )
        
        for cache_entry in cache_entries[:5]:
            origem_normalizada = normalizar_texto(cache_entry.origin)
            destino_normalizada = normalizar_texto(cache_entry.destination)
            
            if (endereco_normalizado in origem_normalizada or 
                endereco in cache_entry.origin):
                print(f"✅ Encontrado no DataCacheRoute como ORIGEM")
                return (float(cache_entry.latitude_origin), 
                       float(cache_entry.longitude_origin))
            elif (endereco_normalizado in destino_normalizada or 
                  endereco in cache_entry.destination):
                print(f"✅ Encontrado no DataCacheRoute como DESTINO") 
                return (float(cache_entry.latitude_destination), 
                       float(cache_entry.longitude_destination))
        
        endereco_upper = endereco.upper()
        
        partes = endereco_upper.split(',')
        rua_numero = partes[0].strip() if partes else endereco_upper
        bairro = partes[1].strip() if len(partes) > 1 else ""
        
        rua_numero_normalizado = normalizar_texto(rua_numero)
        bairro_normalizado = normalizar_texto(bairro)
        
        rua_partes = rua_numero.split(' ')
        numero = None
        rua_sem_numero = rua_numero
        
        for i in range(len(rua_partes)-1, -1, -1):
            if rua_partes[i].replace('.', '').isdigit():
                numero = rua_partes[i]
                rua_sem_numero = ' '.join(rua_partes[:i])
                break
        
        rua_sem_numero_normalizado = normalizar_texto(rua_sem_numero)
        
        queries = [
            models.Q(
                street__iexact=rua_sem_numero,
                number__iexact=numero
            ) if numero else None,
            
            models.Q(street__iexact=rua_numero),
            models.Q(street__iexact=rua_numero_normalizado),
            
            models.Q(
                street__icontains=rua_sem_numero,
                neighborhood__icontains=bairro
            ) if bairro else None,
            models.Q(
                street__icontains=rua_sem_numero_normalizado,
                neighborhood__icontains=bairro_normalizado
            ) if bairro else None,
            
            models.Q(street__icontains=rua_sem_numero),
            models.Q(street__icontains=rua_sem_numero_normalizado),
            
            models.Q(neighborhood__icontains=bairro) if bairro else None,
            models.Q(neighborhood__icontains=bairro_normalizado) if bairro else None,
        ]
        
        for query in [q for q in queries if q is not None]:
            address_obj = Address.objects.filter(query).first()
            if address_obj and address_obj.latitude and address_obj.longitude:
                print(f"✅ Encontrado na tabela Address: {address_obj.street}, {address_obj.number}")
                return (float(address_obj.latitude), float(address_obj.longitude))
        
        if usar_api_fallback and api_key:
            print(f"🔄 Não encontrado no cache, usando API para: {endereco}")
            return fazer_geocoding_api(endereco, api_key)
        
        print(f"❌ Nenhuma coordenada encontrada para: {endereco}")
        return None
        
    except Exception as e:
        print(f"🚨 Erro ao buscar coordenadas: {e}")
        return None