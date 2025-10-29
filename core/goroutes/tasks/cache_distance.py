from celery import shared_task
from core.goroutes.models import DataCacheRoute
from core.authentication.models import Passenger, Address
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import googlemaps
from django.conf import settings
import time
from django.db import transaction
from django.db.models import Count, Avg

@shared_task(bind=True, max_retries=3)
def make_cache_distance_passengers(self, max_passengers=None):
    """
    Task para criar grafo de distâncias entre todos os passageiros usando Distance Matrix API
    """
    try:
        console = Console()
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        console.print(Panel(
            "🌍 INICIANDO CRIAÇÃO DO GRAFO COM DISTANCE MATRIX API",
            style="bold blue"
        ))
        
        # Busca passageiros com endereço principal e coordenadas
        passengers_with_coords = []
        all_passengers = Passenger.objects.all().prefetch_related('address')
        
        if max_passengers:
            all_passengers = all_passengers[:max_passengers]
        
        for passenger in all_passengers:
            main_address = passenger.address.filter(is_main=True).first()
            if not main_address:
                main_address = passenger.address.first()
            
            if main_address and main_address.latitude and main_address.longitude:
                passengers_with_coords.append({
                    'id': passenger.id,
                    'name': passenger.user.name,
                    'address': main_address,
                    'coords': f"{main_address.latitude},{main_address.longitude}",
                    'full_address': main_address.full_address
                })
        
        total_passengers = len(passengers_with_coords)
        
        console.print(Panel(
            f"📊 CONFIGURAÇÃO DO GRAFO\n\n"
            f"🧍 Passageiros com coordenadas: [bold green]{total_passengers}[/bold green]\n"
            f"📦 Pares totais: [bold yellow]{total_passengers * (total_passengers - 1)}[/bold yellow]\n"
            f"🚗 Modo: driving\n"
            f"📏 Unidades: metric",
            style="green"
        ))
        
        if total_passengers < 2:
            console.print("[red]❌ Necessário pelo menos 2 passageiros com coordenadas[/red]")
            return {
                'status': 'error',
                'message': 'Necessário pelo menos 2 passageiros com coordenadas'
            }
        
        # Calcula distâncias entre todos os pares
        total_pairs = total_passengers * (total_passengers - 1)
        pairs_processed = 0
        routes_cached = 0
        errors = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Calculando distâncias...", total=total_pairs)
            
            # Para cada passageiro como origem
            for i, origin in enumerate(passengers_with_coords):
                destinations = [dest for j, dest in enumerate(passengers_with_coords) if i != j]
                
                console.print(f"\n📍 Origem: [bold]{origin['name']}[/bold]")
                console.print(f"   🎯 Destinos: {len(destinations)} passageiros")
                
                # Processa destinos em lotes de 25 (limite da Distance Matrix API)
                for batch_start in range(0, len(destinations), 25):
                    batch_destinations = destinations[batch_start:batch_start + 25]
                    batch_size = len(batch_destinations)
                    
                    try:
                        # 🎯 CHAMA DISTANCE MATRIX API
                        matrix_result = gmaps.distance_matrix(
                            origins=[origin['coords']],
                            destinations=[dest['coords'] for dest in batch_destinations],
                            mode="driving",
                            language="pt-BR",
                            units="metric"
                        )
                        
                        # Processa resultados do batch
                        for j, destination in enumerate(batch_destinations):
                            try:
                                element = matrix_result['rows'][0]['elements'][j]
                                
                                if element['status'] == 'OK':
                                    distance = element['distance']['value']  # metros
                                    duration = element['duration']['value']   # segundos
                                    
                                    # 🗄️ Salva no cache
                                    with transaction.atomic():
                                        DataCacheRoute.objects.update_or_create(
                                            origin=origin['full_address'],
                                            destination=destination['full_address'],
                                            defaults={
                                                'distance': distance,
                                                'duration': duration,
                                                'latitude_origin': origin['address'].latitude,
                                                'longitude_origin': origin['address'].longitude,
                                                'latitude_destination': destination['address'].latitude,
                                                'longitude_destination': destination['address'].longitude,
                                                'polyline': ""  # Distance Matrix não retorna polyline
                                            }
                                        )
                                    
                                    routes_cached += 1
                                    
                                    # Log a cada 10 rotas para não poluir muito
                                    if routes_cached % 10 == 0:
                                        console.print(f"   ✅ [dim]Cache: {routes_cached} rotas[/dim]")
                                
                                else:
                                    console.print(f"   ❌ [red]Erro na rota: {element['status']}[/red]")
                                    errors += 1
                                
                                pairs_processed += 1
                                progress.update(task, advance=1)
                                
                            except Exception as e:
                                errors += 1
                                pairs_processed += 1
                                progress.update(task, advance=1)
                                console.print(f"   ❌ [red]Erro processando destino {j}: {str(e)}[/red]")
                        
                        # ⏰ Delay para respeitar limites da API
                        time.sleep(0.2)
                        
                        console.print(f"   🔄 [dim]Batch {batch_start//25 + 1} concluído ({batch_size} destinos)[/dim]")
                        
                    except Exception as e:
                        errors += batch_size
                        pairs_processed += batch_size
                        progress.update(task, advance=batch_size)
                        console.print(f"   ❌ [red]Erro no batch: {str(e)}[/red]")
        
        # 📊 Resultado final
        console.print(Panel(
            f"🎉 GRAFO DE DISTÂNCIAS CONCLUÍDO!\n\n"
            f"✅ Pares processados: {pairs_processed}/{total_pairs}\n"
            f"🗄️  Rotas em cache: {routes_cached}\n"
            f"❌ Erros: {errors}\n"
            f"📈 Eficiência: {((routes_cached / total_pairs) * 100):.1f}%",
            style="bold green"
        ))
        
        # Mostra estatísticas do cache
        cache_stats = DataCacheRoute.objects.aggregate(
            total_routes=Count('id'),
            avg_distance=Avg('distance'),
            avg_duration=Avg('duration')
        )
        
        console.print(Panel(
            f"📈 ESTATÍSTICAS DO CACHE\n\n"
            f"🗂️  Total de rotas salvas: {cache_stats['total_routes']}\n"
            f"📏 Distância média: {cache_stats['avg_distance']:.0f} metros\n"
            f"⏱️  Duração média: {cache_stats['avg_duration']:.0f} segundos",
            style="blue"
        ))
        
        return {
            'status': 'success',
            'total_passengers': total_passengers,
            'total_pairs': total_pairs,
            'pairs_processed': pairs_processed,
            'routes_cached': routes_cached,
            'errors': errors,
            'cache_stats': cache_stats
        }
        
    except Exception as e:
        console.print(f"[red]❌ Erro na task create_distance_graph: {str(e)}[/red]")
        self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=3)
def create_distance_graph_small(self):
    """
    Versão para teste com poucos passageiros
    """
    return make_cache_distance_passengers(self, max_passengers=10)