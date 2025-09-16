import requests
import time
import logging
import numpy as np
from sklearn.cluster import KMeans
from urllib.parse import quote_plus
import os
import json

# Imports externos
from .optimize_route import verificar_enderecos, obter_coordenadas, verificar_endereco_individual 

try:
    from django.conf import settings
except ImportError:
    settings = None


class OtimizadorRotas:
    """
    Classe para otimizar rotas de vans, considerando os endereços iniciais das vans.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def otimizar_rotas(self, enderecos, endereco_final, vans):
        """
        Otimiza as rotas das vans, considerando os endereços iniciais de cada van.
        """
        cidade_padrao = "Joinville, SC, Brasil"

        # Normalizar endereços de passageiros
        enderecos_completos = []
        for endereco in enderecos:
            if "JOINVILLE" not in endereco['local'].upper() and "SC" not in endereco['local'].upper():
                endereco_completo = f"{endereco['local']}, {cidade_padrao}"
            else:
                endereco_completo = endereco['local']
            
            enderecos_completos.append({
                'local': endereco_completo,
                'passageiros': endereco['passageiros']
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

        # 🔹 Verificar todos os endereços
        todos_enderecos = [van['endereco_inicial'] for van in vans_completos] + [endereco_final] + [e['local'] for e in enderecos_completos]
        verificar_enderecos(todos_enderecos, self.api_key)

        # Obter coordenadas das vans
        van_coords = []
        for van in vans_completos:
            coord = obter_coordenadas(van['endereco_inicial'], self.api_key)
            van_coords.append(coord)
            time.sleep(0.1)

        # Obter coordenadas dos passageiros
        enderecos_com_coords = []
        for endereco in enderecos_completos:
            coord = obter_coordenadas(endereco['local'], self.api_key)
            enderecos_com_coords.append({
                'indice': len(enderecos_com_coords),
                'endereco': endereco,
                'coords': coord
            })
            time.sleep(0.1)

        coords_passageiros = np.array([e['coords'] for e in enderecos_com_coords])
        if len(coords_passageiros) == 0:
            return []

        # Clustering (K-Means)
        n_clusters = min(len(vans_completos), len(coords_passageiros))
        if len(van_coords) < n_clusters:
            logging.warning(f"Número de coordenadas de vans ({len(van_coords)}) menor que clusters ({n_clusters})")
            n_clusters = len(van_coords) if van_coords else 1

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
                'enderecos': [e['endereco']['local'] for e in grupo_enderecos]
            })

        # Consultar Google Directions API
        rotas_finais = []
        for grupo in grupos_por_van:
            waypoints = grupo['enderecos']
            if not waypoints:
                continue

            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': grupo['endereco_inicial'],
                'destination': endereco_final,
                'waypoints': 'optimize:true|' + '|'.join(waypoints),
                'region': 'br',
                'language': 'pt-BR',
                'key': self.api_key
            }

            try:
                response = requests.get(url, params=params)
                data = response.json()

                # Salvar resposta em JSON
                try:
                    base_dir = getattr(settings, 'BASE_DIR', None) if settings else None
                    if not base_dir:
                        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    file_name = f"data_van_{grupo['van_id']}.json"
                    file_path = os.path.join(base_dir, file_name)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                    logging.info(f"Dados da API salvos em {file_path}")
                except Exception as e:
                    logging.error(f"Erro ao salvar dados da API: {e}")

                if data['status'] == 'OK':
                    rota = data['routes'][0]
                    legs = rota['legs']

                    caminho = [grupo['endereco_inicial']]
                    if 'waypoint_order' in rota:
                        ordem_otimizada = rota['waypoint_order']
                        caminho.extend([waypoints[i] for i in ordem_otimizada])
                    else:
                        caminho.extend(waypoints)
                    caminho.append(endereco_final)

                    distancia_total = sum(leg['distance']['value'] for leg in legs)
                    tempo_total = sum(leg['duration']['value'] for leg in legs)

                    link_maps = self.gerar_link_maps(caminho)

                    rotas_finais.append({
                        'van_id': grupo['van_id'],
                        'caminho': caminho,
                        'distancia_total': distancia_total,
                        'tempo_estimado': tempo_total,
                        'link_maps': link_maps,
                        'coords_passageiros': coords_passageiros.tolist()
                    })

            except Exception as e:
                logging.error(f"Erro ao processar rota da van {grupo['van_id']}: {str(e)}")

            time.sleep(0.2)

        return rotas_finais

    def gerar_link_maps(self, caminho):
        """
        Gera um link do Google Maps com a rota otimizada.
        """
        if not caminho or len(caminho) < 2:
            raise ValueError("Caminho insuficiente para gerar a rota.")

        def limpar_endereco(endereco: str) -> str:
            return endereco.replace('#', '').replace('&', '')

        origin = limpar_endereco(caminho[0])
        destination = limpar_endereco(caminho[-1])
        waypoints = [limpar_endereco(p) for p in caminho[1:-1]]

        base_url = "https://www.google.com/maps/dir/"

        params = {
            "api": "1",
            "origin": origin,
            "destination": destination,
            "travelmode": "driving"
        }

        if waypoints:
            params["waypoints"] = "|".join(waypoints)

        query = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        return f"{base_url}?{query}"

    def verificar_endereco_individual(self, endereco: str):
        """
        Wrapper para usar a função externa verificar_endereco_individual
        """
        return verificar_endereco_individual(endereco, self.api_key)


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


from typing import List, Dict, Any

def otimizar_rotas_vans(enderecos: List[Dict[str, Any]], 
                        endereco_final: str, 
                        vans: List[Dict[str, Any]], 
                        api_key: str) -> List[Dict[str, Any]]:
    """
    Função principal para otimizar rotas de vans.

    Args:
        enderecos: Lista de dicionários com 'local' (string) e 'passageiros' (int).
        endereco_final: Endereço final das vans.
        vans: Lista de dicionários de vans disponíveis, com 'van', 'lugares' e 'endereco_inicial'.
        api_key: Chave da API do Google Maps.

    Returns:
        Lista de rotas otimizadas para cada van, com link para o Google Maps.
    """
    print(enderecos)
    print(endereco_final)
    print(vans)
    print(api_key)
    otimizador = OtimizadorRotas(api_key)
    return otimizador.otimizar_rotas(enderecos, endereco_final, vans)
