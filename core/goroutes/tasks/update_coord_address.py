from celery import shared_task
from core.authentication.models import Address
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import googlemaps
from django.conf import settings
import time
from django.db import models

@shared_task(bind=True, max_retries=3)
def geocode_all_addresses(self, delay_between_requests=0.1):
    """
    Task para geocodificar TODOS os endereços via API do Google Maps
    """
    try:
        console = Console()
        
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        addresses_without_coords = Address.objects.filter(
            models.Q(latitude__isnull=True) | 
            models.Q(latitude='') |
            models.Q(longitude__isnull=True) | 
            models.Q(longitude='')
        )
        
        total_addresses = addresses_without_coords.count()
        
        console.print(Panel(
            f"🌍 GEOCODIFICANDO TODOS OS ENDEREÇOS\n\n"
            f"Total de endereços sem coordenadas: [bold yellow]{total_addresses}[/bold yellow]\n"
            f"Delay entre requests: {delay_between_requests}s",
            title="GOOGLE MAPS GEOCODING - TODOS OS ENDEREÇOS",
            style="blue"
        ))
        
        if total_addresses == 0:
            console.print("[green]✅ Todos os endereços já possuem coordenadas![/green]")
            return {
                'status': 'success',
                'message': 'Todos os endereços já possuem coordenadas',
                'processed': 0,
                'updated': 0,
                'errors': 0
            }
        
        processed = 0
        updated = 0
        errors = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task("Geocodificando TODOS os endereços...", total=total_addresses)
            
            for address in addresses_without_coords:
                try:
                    full_address = address.full_address
                    
                    geocode_result = gmaps.geocode(full_address)
                    
                    if geocode_result:
                        location = geocode_result[0]['geometry']['location']
                        latitude = location['lat']
                        longitude = location['lng']
                        
                        address.latitude = str(latitude)
                        address.longitude = str(longitude)
                        address.save()
                        
                        updated += 1
                        console.print(f"  ✅ [green]{address.full_address}[/green]")
                        console.print(f"     📍 Lat: {latitude}, Lng: {longitude}")
                    else:
                        errors += 1
                        console.print(f"  ❌ [red]Endereço não encontrado: {full_address}[/red]")
                    
                    processed += 1
                    progress.update(task, advance=1)
                    
                    time.sleep(delay_between_requests)
                    
                except Exception as e:
                    errors += 1
                    processed += 1
                    console.print(f"  ❌ [red]Erro no endereço {address.id}: {str(e)}[/red]")
                    progress.update(task, advance=1)
        
        console.print(Panel(
            f"📊 RESULTADO FINAL DA GEOCODIFICAÇÃO\n\n"
            f"✅ Total processados: {processed}/{total_addresses}\n"
            f"🔄 Total atualizados: {updated}\n"
            f"❌ Total erros: {errors}",
            style="green" if errors == 0 else "yellow"
        ))
        
        return {
            'status': 'success',
            'total_addresses': total_addresses,
            'processed': processed,
            'updated': updated,
            'errors': errors
        }
        
    except Exception as e:
        console.print(f"[red]Erro na task geocode_all_addresses: {str(e)}[/red]")
        self.retry(countdown=300, exc=e)