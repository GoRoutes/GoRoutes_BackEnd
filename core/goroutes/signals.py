import json
import logging
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from core.goroutes.models import Route, PassengerRoute
from core.goroutes.utils.auto_route import otimizar_rotas_vans
from core.authentication.models import Passenger

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Route)
def set_start_address(sender, instance, **kwargs):
    """
    Signal to set the start address of a route to the driver's address if not provided.
    Returns True if route optimization was successful or not needed,
    Returns False if optimization failed and the route should not be saved.
    """
    if instance.auto_recalculate:
        logger.info("Iniciando cálculo automático de rota")
        try:
            # Se não tiver endereços explícitos, pegar dos passageiros
            if not instance.addresses:
                # Pegar os passageiros da rota
                passenger_ids = PassengerRoute.objects.filter(route=instance).values_list('passenger_id', flat=True)
                passengers = Passenger.objects.filter(id__in=passenger_ids).prefetch_related('address')
                
                if not passengers.exists():
                    logger.error("Nenhum passageiro encontrado para a rota")
                    return False
                
                # Pegar os endereços principais dos passageiros
                addresses = []
                for passenger in passengers:
                    main_address = passenger.address.filter(is_main=True).first()
                    if main_address:
                        full_address = f"{main_address.street}, {main_address.number} - {main_address.neighborhood}, {main_address.city} - {main_address.state}"
                        addresses.append({"local": full_address, "passageiros": 1})
                    else:
                        logger.warning(f"Passageiro {passenger.id} não tem endereço principal")
                
                if not addresses:
                    logger.error("Nenhum endereço principal encontrado para os passageiros")
                    return False
                
                logger.info(f"Usando {len(addresses)} endereços dos passageiros")
            else:
                # Usar os endereços explícitos
                raw_enderecos = instance.addresses
                addresses = []
                for endereco in raw_enderecos:
                    if isinstance(endereco, str):
                        addresses.append({"local": endereco, "passageiros": 1})
                    else:
                        addresses.append({"local": str(endereco), "passageiros": 1})
                
                if not addresses:
                    logger.error("Lista de endereços explícitos está vazia")
                    return False
                
                logger.info(f"Usando {len(addresses)} endereços explícitos")
            
        except Exception as e:
            logger.error(f"Erro ao processar endereços: {e}")
            return False

        # Usar origin e destination ao invés de start_address e final_address
        endereco_inicial = instance.origin
        endereco_final = instance.destination

        # Verificar se tem veículo antes de tentar acessar
        if instance.vehicle:
            van_info = {"van": instance.vehicle.id, "lugares": instance.vehicle.seats, "endereco_inicial": endereco_inicial}
            vans = [van_info]
        else:
            logger.error("Veículo não definido para a rota")
            return False

        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if api_key is None:
            logger.error("API key do Google Maps não encontrada")
            return False
            
        try:
            logger.info(f"Otimizando rotas para {len(addresses)} endereços")
            
            rotas_otimizadas = otimizar_rotas_vans(
                addresses,
                endereco_final,
                vans,
                api_key
            )
            
            if rotas_otimizadas and len(rotas_otimizadas) > 0:
                # Serializar com ensure_ascii=False para preservar caracteres especiais
                instance.addresses_order = json.dumps(
                    rotas_otimizadas[0]['caminho'], 
                    ensure_ascii=False
                )
                instance.distance = rotas_otimizadas[0]['distancia_total']
                instance.optimized_route_url = rotas_otimizadas[0]['link_maps']
                
                logger.info(f"Rota otimizada com sucesso: {len(rotas_otimizadas[0]['caminho'])} paradas")
                return True
            else:
                logger.error("Nenhuma rota otimizada foi retornada")
                return False
                
        except IndexError as e:
            logger.error(f"Erro ao acessar resultados da otimização: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao otimizar rotas: {e}")
            return False
    
    return True  # Se não precisar otimizar, retorna True



