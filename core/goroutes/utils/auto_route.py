import requests
import time
from typing import List, Dict, Any
from urllib.parse import quote_plus
import logging
from sklearn.cluster import KMeans
import numpy as np
import os
import json

# Tentativa de importar o Django settings
try:
    from django.conf import settings
except ImportError:
    settings = None

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

class OtimizadorRotas:
    """
    Classe para otimizar rotas de vans, considerando os endereços iniciais das vans.
    """

    def __init__(self, api_key: str):
        """
        Inicializa o otimizador de rotas com a chave da API do Google Maps.

        Args:
            api_key: Chave da API do Google Maps.
        """
        self.api_key = api_key

    def verificar_enderecos(self, enderecos: List[str]) -> Dict[str, bool]:
        """
        Verifica se os endereços existem utilizando a API de Geocodificação do Google Maps.

        Args:
            enderecos: Lista de endereços a serem verificados.

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
                    'key': self.api_key
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

    def obter_coordenadas(self, endereco: str) -> List[float]:
        """
        Obtém as coordenadas (latitude, longitude) de um endereço.

        Args:
            endereco: Endereço para obter as coordenadas.

        Returns:
            Lista com latitude e longitude.
        """
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {'address': endereco, 'key': self.api_key}
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

    def otimizar_rotas(self, enderecos: List[Dict[str, Any]], endereco_final: str, vans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Otimiza as rotas das vans, considerando os endereços iniciais de cada van.

        Args:
            enderecos: Lista de dicionários com 'local' (string) e 'passageiros' (int).
            endereco_final: Endereço final das vans.
            vans: Lista de dicionários de vans disponíveis, com 'van', 'lugares' e 'endereco_inicial'.

        Returns:
            Lista de rotas otimizadas para cada van, com link para o Google Maps.
        """
        # Primeiro, complete os endereços com a cidade/estado
        cidade_padrao = "Joinville, SC, Brasil"
        
        enderecos_completos = []
        for endereco in enderecos:
            # Verifica se o endereço já tem cidade/estado
            if "JOINVILLE" not in endereco['local'].upper() and "SC" not in endereco['local'].upper():
                endereco_completo = f"{endereco['local']}, {cidade_padrao}"
            else:
                endereco_completo = endereco['local']
            
            enderecos_completos.append({
                'local': endereco_completo,
                'passageiros': endereco['passageiros']
            })
        
        # Complete também os endereços das vans e destino final
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
        
        if "ARAQUARI" not in endereco_final.upper() and "SC" not in endereco_final.upper():
            endereco_final = f"{endereco_final}, Araquari, SC, Brasil"
        
        # Verificar todos os endereços
        todos_enderecos = [van['endereco_inicial'] for van in vans_completos] + [endereco_final] + [e['local'] for e in enderecos_completos]
        self.verificar_enderecos(todos_enderecos)

        # Obter coordenadas das vans
        van_coords = []
        for van in vans_completos:
            coord = self.obter_coordenadas(van['endereco_inicial'])
            van_coords.append(coord)
            time.sleep(0.1)  # Respeitar limites da API

        # Obter coordenadas dos endereços dos passageiros
        enderecos_com_coords = []
        for endereco in enderecos_completos:
            coord = self.obter_coordenadas(endereco['local'])
            enderecos_com_coords.append({
                'indice': len(enderecos_com_coords),
                'endereco': endereco,
                'coords': coord
            })
            time.sleep(0.1)  # Respeitar limites da API

        coords_passageiros = np.array([e['coords'] for e in enderecos_com_coords])
        print(coords_passageiros)
        if len(coords_passageiros) == 0:
            return []

        # Configurar K-means com centros nas vans
        n_clusters = min(len(vans_completos), len(coords_passageiros))
        if len(van_coords) < n_clusters:
            logging.warning(f"Número de coordenadas de vans ({len(van_coords)}) menor que clusters ({n_clusters})")
            n_clusters = len(van_coords) if van_coords else 1

        kmeans = KMeans(n_clusters=n_clusters, init=np.array(van_coords[:n_clusters]), n_init=1)
        clusters = kmeans.fit_predict(coords_passageiros)

        # Agrupar endereços por van e verificar capacidade
        grupos_por_van = []
        for i in range(n_clusters):
            # Índices dos passageiros neste cluster
            indices = [j for j, cluster_id in enumerate(clusters) if cluster_id == i]
            grupo_enderecos = [enderecos_com_coords[j] for j in indices]

            # Verificar capacidade da van
            van = vans_completos[i]
            total_passageiros = sum(e['endereco']['passageiros'] for e in grupo_enderecos)
            if total_passageiros > van['lugares']:
                raise ValueError(f"Van {van['van']} excedeu a capacidade: {total_passageiros} > {van['lugares']}")

            grupos_por_van.append({
                'van_id': van['van'],
                'endereco_inicial': van['endereco_inicial'],
                'enderecos': [e['endereco']['local'] for e in grupo_enderecos]
            })

        # Otimizar rotas para cada van
        rotas_finais = []
        for grupo in grupos_por_van:
            waypoints = grupo['enderecos']
            if not waypoints:
                print("Grupo vazio, ignorando.")
                continue  # Ignorar vans sem endereços

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

                # Salvar resposta da API corretamente em formato JSON
                try:
                    # Obter o diretório do projeto
                    if settings:
                        base_dir = getattr(settings, 'BASE_DIR', None)
                    else:
                        base_dir = None
                    
                    if not base_dir:
                        # Fallback para o diretório atual
                        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    # Usar um nome de arquivo que inclui o ID da van
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

                    # Construir caminho completo
                    caminho = [grupo['endereco_inicial']]
                    if 'waypoint_order' in rota:
                        ordem_otimizada = rota['waypoint_order']
                        caminho.extend([waypoints[i] for i in ordem_otimizada])
                    else:
                        caminho.extend(waypoints)
                    caminho.append(endereco_final)

                    # Calcular distância e tempo
                    distancia_total = sum(leg['distance']['value'] for leg in legs)
                    tempo_total = sum(leg['duration']['value'] for leg in legs)

                    # Gerar link do Maps
                    link_maps = self.gerar_link_maps(caminho)

                    rotas_finais.append({
                        'van_id': grupo['van_id'],
                        'caminho': caminho,
                        'distancia_total': distancia_total,
                        'tempo_estimado': tempo_total,
                        'link_maps': link_maps
                    })
                elif data['status'] == 'ZERO_RESULTS':
                    logging.error(f"Não foi possível encontrar rota entre {grupo['endereco_inicial']} e {endereco_final} com os waypoints fornecidos")
                    
                    # Tente uma abordagem alternativa com menos waypoints
                    if len(waypoints) > 5:
                        logging.info("Tentando com menos waypoints...")
                        # Divida em grupos menores
                        chunks = [waypoints[i:i+5] for i in range(0, len(waypoints), 5)]
                        rotas_parciais = []
                        
                        for chunk in chunks:
                            params_chunk = {
                                'origin': grupo['endereco_inicial'] if not rotas_parciais else rotas_parciais[-1][-1],
                                'destination': endereco_final if chunk == chunks[-1] else chunk[-1],
                                'waypoints': 'optimize:true|' + '|'.join(chunk[:-1]) if chunk != chunks[-1] else 'optimize:true|' + '|'.join(chunk),
                                'region': 'br',
                                'language': 'pt-BR',
                                'key': self.api_key
                            }
                            
                            # Faz a requisição com o chunk
                            # ... implementar lógica para processar cada chunk
                time.sleep(0.2)  # Respeitar limites da API
            except Exception as e:
                logging.error(f"Erro ao processar rota da van {grupo['van_id']}: {str(e)}")

        return rotas_finais

    def gerar_link_maps(self, caminho: List[str]) -> str:
        """
        Gera um link do Google Maps com a rota otimizada.

        Args:
            caminho: Lista de endereços no caminho, onde o primeiro é a origem e o último o destino.

        Returns:
            Link do Google Maps com a rota.
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

    def verificar_endereco_individual(self, endereco: str) -> Dict:
        """Verifica um único endereço e retorna informações detalhadas."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': endereco,
            'region': 'br',
            'language': 'pt-BR',
            'key': self.api_key
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
