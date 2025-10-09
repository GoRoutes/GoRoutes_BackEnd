from sklearn.cluster import KMeans
from typing import List, Dict, Any
from rich import print
from rich.pretty import Pretty
from rich.panel import Panel
from rich.text import Text
import requests
import time
import logging
import numpy as np
import os
import json
import googlemaps
from django.db import models
import unicodedata

try:
    from django.conf import settings
    from core.goroutes.models import DataCacheRoute
    from core.authentication.models import Address
except ImportError:
    settings = None

class OtimizadorRotas:
    """
    Classe para otimizar rotas de vans, usando CACHE com fallback para API
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def normalizar_texto(self, texto: str) -> str:
        """
        Remove acentos e normaliza texto para busca
        """
        # Remove acentos
        texto_sem_acentos = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        # Coloca em maiúsculas e remove espaços extras
        texto_sem_acentos = texto_sem_acentos.upper().strip()
        # Normaliza padrões comuns
        texto_sem_acentos = texto_sem_acentos.replace('RUA:', 'RUA')
        texto_sem_acentos = texto_sem_acentos.replace('SERVIDÃO', 'SERV')
        texto_sem_acentos = texto_sem_acentos.replace('AV.', 'AVENIDA')
        texto_sem_acentos = texto_sem_acentos.replace('AV ', 'AVENIDA ')
        return texto_sem_acentos

    def obter_coordenadas_do_cache(self, endereco: str, usar_api_fallback=True):
        """
        Busca coordenadas - com tratamento de acentos
        """
        try:
            print(f"🔍 Buscando coordenadas para: {endereco}")
            
            endereco_normalizado = self.normalizar_texto(endereco)
            
            # 1. Tenta no DataCacheRoute (cache de rotas) - com e sem acentos
            cache_entries = DataCacheRoute.objects.filter(
                models.Q(origin__icontains=endereco) |
                models.Q(destination__icontains=endereco) |
                models.Q(origin__icontains=endereco_normalizado) |
                models.Q(destination__icontains=endereco_normalizado)
            )
            
            for cache_entry in cache_entries[:5]:
                origem_normalizada = self.normalizar_texto(cache_entry.origin)
                destino_normalizada = self.normalizar_texto(cache_entry.destination)
                
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
            
            # 2. Tenta na tabela Address - busca mais robusta
            endereco_upper = endereco.upper()
            
            # Extrai partes do endereço
            partes = endereco_upper.split(',')
            rua_numero = partes[0].strip() if partes else endereco_upper
            bairro = partes[1].strip() if len(partes) > 1 else ""
            
            # Normaliza as partes
            rua_numero_normalizado = self.normalizar_texto(rua_numero)
            bairro_normalizado = self.normalizar_texto(bairro)
            
            # Separa rua e número
            rua_partes = rua_numero.split(' ')
            numero = None
            rua_sem_numero = rua_numero
            
            for i in range(len(rua_partes)-1, -1, -1):
                if rua_partes[i].replace('.', '').isdigit():
                    numero = rua_partes[i]
                    rua_sem_numero = ' '.join(rua_partes[:i])
                    break
            
            rua_sem_numero_normalizado = self.normalizar_texto(rua_sem_numero)
            
            # Busca por diferentes critérios (com e sem acentos)
            queries = [
                # Busca exata com número
                models.Q(
                    street__iexact=rua_sem_numero,
                    number__iexact=numero
                ) if numero else None,
                
                # Busca por rua completa
                models.Q(street__iexact=rua_numero),
                models.Q(street__iexact=rua_numero_normalizado),
                
                # Busca por parte da rua + bairro
                models.Q(
                    street__icontains=rua_sem_numero,
                    neighborhood__icontains=bairro
                ) if bairro else None,
                models.Q(
                    street__icontains=rua_sem_numero_normalizado,
                    neighborhood__icontains=bairro_normalizado
                ) if bairro else None,
                
                # Busca apenas pela rua
                models.Q(street__icontains=rua_sem_numero),
                models.Q(street__icontains=rua_sem_numero_normalizado),
                
                # Busca apenas pelo bairro (último recurso)
                models.Q(neighborhood__icontains=bairro) if bairro else None,
                models.Q(neighborhood__icontains=bairro_normalizado) if bairro else None,
            ]
            
            # Remove queries None e executa
            for query in [q for q in queries if q is not None]:
                address_obj = Address.objects.filter(query).first()
                if address_obj and address_obj.latitude and address_obj.longitude:
                    print(f"✅ Encontrado na tabela Address: {address_obj.street}, {address_obj.number}")
                    return (float(address_obj.latitude), float(address_obj.longitude))
            
            # 3. SE NÃO ENCONTROU E É PERMITIDO USAR API, FAZ GEOCODING
            if usar_api_fallback and self.api_key:
                print(f"🔄 Não encontrado no cache, usando API para: {endereco}")
                return self.fazer_geocoding_api(endereco)
            
            print(f"❌ Nenhuma coordenada encontrada para: {endereco}")
            return None
            
        except Exception as e:
            print(f"🚨 Erro ao buscar coordenadas: {e}")
            return None

    def fazer_geocoding_api(self, endereco: str):
        """
        Faz geocoding via API Google como fallback
        """
        try:
            gmaps = googlemaps.Client(key=self.api_key)
            
            geocode_result = gmaps.geocode(endereco)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
                
                print(f"📍 API retornou coordenadas: {latitude}, {longitude}")
                
                # Salva no cache para próximas consultas
                self.salvar_coordenadas_no_cache(endereco, latitude, longitude)
                
                return (latitude, longitude)
            else:
                print(f"❌ API não encontrou endereço: {endereco}")
                return None
                
        except Exception as e:
            print(f"🚨 Erro na API Geocoding: {e}")
            return None

    def salvar_coordenadas_no_cache(self, endereco: str, lat: float, lng: float):
        """
        Salva coordenadas no Address para cache futuro
        """
        try:
            # Extrai partes do endereço
            partes = endereco.split(',')
            rua_numero = partes[0].strip() if partes else endereco
            bairro = partes[1].strip() if len(partes) > 1 else "Desconhecido"
            
            # Separa rua e número
            rua_partes = rua_numero.split(' ')
            numero = None
            rua_sem_numero = rua_numero
            
            for i in range(len(rua_partes)-1, -1, -1):
                if rua_partes[i].replace('.', '').isdigit():
                    numero = rua_partes[i]
                    rua_sem_numero = ' '.join(rua_partes[:i])
                    break
            
            # Normaliza para salvar sem acentos
            rua_sem_numero_normalizada = self.normalizar_texto(rua_sem_numero)
            bairro_normalizado = self.normalizar_texto(bairro)
            
            # Tenta encontrar ou criar um Address para este endereço
            address, created = Address.objects.get_or_create(
                street=rua_sem_numero_normalizada,
                number=numero or '0',
                neighborhood=bairro_normalizado or "DESCONHECIDO",
                city="JOINVILLE",
                state="SC",
                defaults={
                    'cep': '00000-000',
                    'complement': '',
                    'latitude': str(lat),
                    'longitude': str(lng),
                    'is_main': False
                }
            )
            
            if created:
                print(f"💾 Novo Address criado no cache: {endereco}")
            else:
                # Atualiza coordenadas se já existia
                address.latitude = str(lat)
                address.longitude = str(lng)
                address.save()
                print(f"💾 Coordenadas atualizadas no cache: {endereco}")
                
        except Exception as e:
            print(f"⚠️ Não foi possível salvar no cache: {e}")

    def calcular_distancia_do_cache(self, origem: str, destino: str):
        """
        Busca distância e duração do cache - COM FALLBACK PARA API
        """
        try:
            print(f"🔍 Buscando distância: {origem} -> {destino}")
            
            origem_normalizada = self.normalizar_texto(origem)
            destino_normalizada = self.normalizar_texto(destino)
            
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
                cache_origem_normalizada = self.normalizar_texto(cache_entry.origin)
                cache_destino_normalizada = self.normalizar_texto(cache_entry.destination)
                
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
            
            # SE NÃO ENCONTROU NO CACHE, USA API
            print(f"🔄 Distância não encontrada no cache, usando API...")
            return self.calcular_distancia_api(origem, destino)
            
        except Exception as e:
            print(f"🚨 Erro ao buscar distância: {e}")
            return None

    def calcular_distancia_api(self, origem: str, destino: str):
        """
        Calcula distância usando Google Distance Matrix API como fallback
        """
        try:
            if not self.api_key:
                print(f"❌ API Key não configurada para fallback")
                return None
            
            print(f"📍 Calculando via API: {origem} -> {destino}")
            
            gmaps = googlemaps.Client(key=self.api_key)
            
            # Chama Distance Matrix API
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
                    distance = element['distance']['value']  # metros
                    duration = element['duration']['value']   # segundos
                    
                    print(f"✅ API retornou: {distance}m, {duration}s")
                    
                    # Salva no cache para futuras consultas
                    self.salvar_distancia_no_cache(origem, destino, distance, duration)
                    
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

    def salvar_distancia_no_cache(self, origem: str, destino: str, distance: int, duration: int):
        """
        Salva distância calculada no DataCacheRoute para futuras consultas
        """
        try:
            # Obtém coordenadas para salvar também
            coord_origem = self.obter_coordenadas_do_cache(origem, usar_api_fallback=True)
            coord_destino = self.obter_coordenadas_do_cache(destino, usar_api_fallback=True)
            
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

    def enderecos_coincidem(self, endereco1: str, endereco2: str) -> bool:
        """
        Compara dois endereços de forma flexível para encontrar correspondência
        """
        def normalizar_endereco_completo(endereco: str) -> str:
            """Normaliza endereço para comparação"""
            # Remove acentos
            texto_sem_acentos = ''.join(
                c for c in unicodedata.normalize('NFD', endereco)
                if unicodedata.category(c) != 'Mn'
            )
            
            # Coloca em maiúsculas e remove caracteres especiais
            texto = texto_sem_acentos.upper()
            import re
            texto = re.sub(r'[^\w\s]', '', texto)
            texto = re.sub(r'\s+', ' ', texto).strip()
            
            # Normaliza padrões comuns
            texto = texto.replace('RUA ', '').replace('AVENIDA ', '').replace('AV ', '')
            texto = texto.replace(' - ', ' ').replace(',', '')
            
            return texto
        
        endereco1_normalizado = normalizar_endereco_completo(endereco1)
        endereco2_normalizado = normalizar_endereco_completo(endereco2)
        
        # Verifica se um endereço contém o outro (para maior flexibilidade)
        return (endereco1_normalizado in endereco2_normalizado or 
                endereco2_normalizado in endereco1_normalizado or
                endereco1_normalizado == endereco2_normalizado)

    def otimizar_rotas(self, enderecos, endereco_final, vans):
        """
        Otimiza rotas usando CACHE com fallback para API
        """
        cidade_padrao = "Joinville, SC, Brasil"

        # Normalizar endereços de passageiros
        enderecos_completos = []
        for endereco in enderecos:
            endereco_local = endereco['local']
            if "JOINVILLE" not in endereco_local.upper() and "SC" not in endereco_local.upper():
                endereco_completo = f"{endereco_local}, {cidade_padrao}"
            else:
                endereco_completo = endereco_local
            
            enderecos_completos.append({
                'local': endereco_completo,
                'passageiros': endereco['passageiros'],
                'original_data': endereco  # Mantém dados originais para referência
            })

        # Normalizar endereços das vans
        vans_completos = []
        for van in vans:
            endereco_inicial = van['endereco_inicial']
            if "JOINVILLE" not in endereco_inicial.upper() and "SC" not in endereco_inicial.upper():
                endereco_inicial = f"{endereco_inicial}, {cidade_padrao}"
            
            vans_completos.append({
                'van': van['van'],
                'lugares': van['lugares'],
                'endereco_inicial': endereco_inicial
            })

        # Normalizar endereço final
        if "ARAQUARI" not in endereco_final.upper() and "SC" not in endereco_final.upper():
            endereco_final = f"{endereco_final}, Araquari, SC, Brasil"

        print(Panel(
            f"🔄 Usando CACHE para otimização\n"
            f"🧍 Passageiros: {len(enderecos_completos)}\n"
            f"🚐 Vans: {len(vans_completos)}\n"
            f"🔑 API Key: {'✅' if self.api_key else '❌'}",
            style="bold green"
        ))

        # 🔄 OBTER COORDENADAS DO CACHE COM FALLBACK
        van_coords = []
        for van in vans_completos:
            coord = self.obter_coordenadas_do_cache(
                van['endereco_inicial'], 
                usar_api_fallback=True
            )
            if coord:
                van_coords.append(coord)
            else:
                logging.error(f"❌ Não foi possível obter coordenadas para van: {van['endereco_inicial']}")

        # 🔄 COORDENADAS DOS PASSAGEIROS (SEM FALLBACK - SÓ CACHE)
        enderecos_com_coords = []
        enderecos_sem_coords = []
        
        for endereco in enderecos_completos:
            coord = self.obter_coordenadas_do_cache(
                endereco['local'], 
                usar_api_fallback=False
            )
            if coord:
                enderecos_com_coords.append({
                    'indice': len(enderecos_com_coords),
                    'endereco': endereco,
                    'coords': coord
                })
            else:
                enderecos_sem_coords.append(endereco['local'])

        if enderecos_sem_coords:
            print(Panel(
                f"⚠️  {len(enderecos_sem_coords)} endereços sem coordenadas no cache:\n"
                f"{chr(10).join(enderecos_sem_coords[:5])}",
                style="yellow"
            ))

        if len(enderecos_com_coords) == 0:
            print("❌ Nenhum passageiro com coordenadas disponíveis")
            return []

        coords_passageiros = np.array([e['coords'] for e in enderecos_com_coords])

        # Clustering (K-Means)
        n_clusters = min(len(vans_completos), len(coords_passageiros))
        if len(van_coords) < n_clusters:
            logging.warning(f"Número de coordenadas de vans ({len(van_coords)}) menor que clusters ({n_clusters})")
            if len(van_coords) == 0:
                kmeans = KMeans(n_clusters=n_clusters, n_init=10)
            else:
                n_clusters = len(van_coords) if van_coords else 1
                kmeans = KMeans(n_clusters=n_clusters, init=np.array(van_coords[:n_clusters]), n_init=1)
        else:
            kmeans = KMeans(n_clusters=n_clusters, init=np.array(van_coords[:n_clusters]), n_init=1)
        
        clusters = kmeans.fit_predict(coords_passageiros)

        # Agrupar endereços por van
        grupos_por_van = []
        for i in range(n_clusters):
            indices = [j for j, cluster_id in enumerate(clusters) if cluster_id == i]
            grupo_enderecos = [enderecos_com_coords[j] for j in indices]

            van = vans_completos[i]
            total_passageiros = sum(e['endereco']['passageiros'] for e in grupo_enderecos)
            if total_passageiros > van['lugares']:
                raise ValueError(f"Van {van['van']} excedeu a capacidade: {total_passageiros} > {van['lugares']}")

            grupos_por_van.append({
                'van_id': van['van'],
                'endereco_inicial': van['endereco_inicial'],
                'enderecos': [e['endereco']['local'] for e in grupo_enderecos],
                'enderecos_com_dados': grupo_enderecos  # Mantém dados completos
            })

        rotas_finais = []
        for grupo in grupos_por_van:
            waypoints = grupo['enderecos']
            if not waypoints:
                continue

            distancia_total = 0
            tempo_total = 0
            caminho = [grupo['endereco_inicial']] + waypoints + [endereco_final]

            # Calcular distâncias entre cada par do caminho
            for i in range(len(caminho) - 1):
                distancia_info = self.calcular_distancia_do_cache(caminho[i], caminho[i + 1])
                if distancia_info:
                    distancia_total += distancia_info['distance']
                    tempo_total += distancia_info['duration']
                else:
                    print(f"❌ Não foi possível calcular distância: {caminho[i]} -> {caminho[i + 1]}")

            link_maps = f"https://www.google.com/maps/dir/{'/'.join([c.replace(' ', '+') for c in caminho])}"

            coords_passageiros_grupo = []
            for endereco_com_dados in grupo['enderecos_com_dados']:
                coord = endereco_com_dados['coords']
                endereco_local = endereco_com_dados['endereco']['local']
                coords_passageiros_grupo.append({
                    'lat': coord[0],
                    'lng': coord[1],
                    'address': endereco_local
                })

            rotas_finais.append({
                'van_id': grupo['van_id'],
                'caminho': caminho,
                'distancia_total': distancia_total,
                'tempo_estimado': tempo_total,
                'link_maps': link_maps,
                'coords_passageiros': coords_passageiros_grupo,
                'enderecos_com_dados': grupo['enderecos_com_dados'], 
                'usando_cache': True
            })

        print(Panel(
            f"✅ Otimização com CACHE concluída!\n"
            f"🚐 Rotas geradas: {len(rotas_finais)}\n"
            f"🧍 Passageiros atendidos: {len(enderecos_com_coords)}\n"
            f"⚡ Velocidade: INSTANTÂNEO",
            style="bold green"
        ))

        return rotas_finais

def otimizar_rotas_vans(enderecos: List[Dict[str, Any]], 
                                endereco_final: str, 
                                vans: List[Dict[str, Any]], 
                                api_key: str = None) -> List[Dict[str, Any]]:

    print(Panel(Pretty(enderecos), title="🧍 Passageiros", style="green"))
    print(Panel(endereco_final, title="🏁 Endereço Final", style="blue"))
    print(Panel(Pretty(vans), title="🚐 Vans", style="magenta"))

    otimizador = OtimizadorRotas(api_key)
    return otimizador.otimizar_rotas(enderecos, endereco_final, vans)

def get_latitude_longitude(address):
    """
    Get latitude and longitude from address using Google Maps API
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None
    except Exception as e:
        print(f"Error getting latitude and longitude: {e}")
        return None, None