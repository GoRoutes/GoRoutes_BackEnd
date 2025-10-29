from django.db import models
from .normalize_text import normalizar_texto
from .calc_distance_api import calcular_distancia_api

try:
    from core.goroutes.models import DataCacheRoute
except ImportError:
    pass

def calcular_distancia_do_cache(api_key: str, obter_coordenadas_do_cache_func, origem: str, destino: str):
    """
    Busca distância e duração do cache - COM FALLBACK PARA API
    """
    try:
        print(f"🔍 Buscando distância: {origem} -> {destino}")
        
        origem_normalizada = normalizar_texto(origem)
        destino_normalizada = normalizar_texto(destino)
        
        def extrair_partes_principais(endereco):
            partes = endereco.split(',')
            if partes:
                rua_numero = partes[0].strip()
                rua_numero = rua_numero.replace('RUA:', '').strip()
                return rua_numero
            return endereco
        
        origem_chave = extrair_partes_principais(origem_normalizada)
        destino_chave = extrair_partes_principais(destino_normalizada)
        
        print(f"   Chaves: '{origem_chave}' -> '{destino_chave}'")
        
        cache_entries = DataCacheRoute.objects.all()
        
        for cache_entry in cache_entries:
            cache_origem_normalizada = normalizar_texto(cache_entry.origin)
            cache_destino_normalizada = normalizar_texto(cache_entry.destination)
            
            cache_origem_chave = extrair_partes_principais(cache_origem_normalizada)
            cache_destino_chave = extrair_partes_principais(cache_destino_normalizada)
            
            match_direta = (
                origem_chave in cache_origem_chave and 
                destino_chave in cache_destino_chave
            )
            
            match_inversa = (
                origem_chave in cache_destino_chave and 
                destino_chave in cache_origem_chave
            )
            
            if match_direta or match_inversa:
                print(f"✅ Distância ENCONTRADA no cache!")
                print(f"   📍 {cache_entry.origin}")
                print(f"   🎯 {cache_entry.destination}")
                print(f"   📏 {cache_entry.distance}m ⏱️ {cache_entry.duration}s")
                return {
                    'distance': cache_entry.distance,
                    'duration': cache_entry.duration
                }
        
        print(f"🔄 Distância não encontrada no cache, usando API...")
        return calcular_distancia_api(api_key, obter_coordenadas_do_cache_func, origem, destino)
        
    except Exception as e:
        print(f"🚨 Erro ao buscar distância: {e}")
        return None