from sklearn.cluster import KMeans
from typing import List, Dict, Any
from rich import print
from rich.pretty import Pretty
from rich.panel import Panel
from rich.text import Text
import logging
import numpy as np

from .optimize_route import obter_coordenadas_do_cache, calcular_distancia_do_cache


from .optimize_route import obter_coordenadas_do_cache, calcular_distancia_do_cache

class OtimizadorRotas:
    """
    Classe para otimizar rotas de vans, usando CACHE com fallback para API
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def obter_coordenadas_do_cache(self, endereco: str, usar_api_fallback=True):
        """
        Wrapper para a função externa obter_coordenadas_do_cache
        """
        return obter_coordenadas_do_cache(self.api_key, endereco, usar_api_fallback)

    def calcular_distancia_do_cache(self, origem: str, destino: str):
        """
        Wrapper para a função externa calcular_distancia_do_cache
        """
        return calcular_distancia_do_cache(self.api_key, self.obter_coordenadas_do_cache, origem, destino)

    def ordenar_waypoints_vizinho_mais_proximo(self, origem_coords, waypoints_com_dados):
        """
        Ordena os waypoints usando a heurística do Vizinho Mais Próximo (Nearest Neighbor).
        """
        if not waypoints_com_dados:
            return []

        waypoints_ordenados = []
        waypoints_restantes = waypoints_com_dados[:]
        ponto_atual = origem_coords

        while waypoints_restantes:
            melhor_vizinho = None
            menor_distancia = float('inf')
            indice_melhor = -1

            for i, waypoint in enumerate(waypoints_restantes):
                coords = waypoint['coords']
                # Distância Euclidiana simples para ordenação (rápida e suficiente para pequenas distâncias)
                # Poderíamos usar haversine, mas para ordenação local euclidiana funciona bem
                dist = (coords[0] - ponto_atual[0])**2 + (coords[1] - ponto_atual[1])**2
                
                if dist < menor_distancia:
                    menor_distancia = dist
                    melhor_vizinho = waypoint
                    indice_melhor = i

            if melhor_vizinho:
                waypoints_ordenados.append(melhor_vizinho)
                ponto_atual = melhor_vizinho['coords']
                waypoints_restantes.pop(indice_melhor)

        return waypoints_ordenados

    def otimizar_rotas(self, enderecos, endereco_final, vans):
        """
        Otimiza rotas usando CACHE com fallback para API
        """
        cidade_padrao = "Joinville, SC, Brasil"

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
                'original_data': endereco 
            })

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

        print(Panel(
            f"🔄 Usando CACHE para otimização\n"
            f"🧍 Passageiros: {len(enderecos_completos)}\n"
            f"🚐 Vans: {len(vans_completos)}\n"
            f"🔑 API Key: {'✅' if self.api_key else '❌'}",
            style="bold green"
        ))

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

        grupos_por_van = []
        for i in range(n_clusters):
            indices = [j for j, cluster_id in enumerate(clusters) if cluster_id == i]
            grupo_enderecos = [enderecos_com_coords[j] for j in indices]

            van = vans_completos[i]
            
            # --- OTIMIZAÇÃO DE ORDEM (Nearest Neighbor) ---
            # Obter coordenada da van (ponto de partida)
            van_coord = None
            if i < len(van_coords):
                van_coord = van_coords[i]
            else:
                # Fallback se não tiver coord da van (improvável se passou na validação acima)
                van_coord = grupo_enderecos[0]['coords'] if grupo_enderecos else (0,0)

            # Reordenar os endereços do grupo
            grupo_enderecos_ordenados = self.ordenar_waypoints_vizinho_mais_proximo(van_coord, grupo_enderecos)
            # ----------------------------------------------

            total_passageiros = sum(e['endereco']['passageiros'] for e in grupo_enderecos_ordenados)
            if total_passageiros > van['lugares']:
                raise ValueError(f"Van {van['van']} excedeu a capacidade: {total_passageiros} > {van['lugares']}")

            grupos_por_van.append({
                'van_id': van['van'],
                'endereco_inicial': van['endereco_inicial'],
                'enderecos': [e['endereco']['local'] for e in grupo_enderecos_ordenados],
                'enderecos_com_dados': grupo_enderecos_ordenados  # Mantém dados completos e ORDENADOS
            })

        rotas_finais = []
        for grupo in grupos_por_van:
            waypoints = grupo['enderecos']
            if not waypoints:
                continue

            distancia_total = 0
            tempo_total = 0
            caminho = [grupo['endereco_inicial']] + waypoints + [endereco_final]

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