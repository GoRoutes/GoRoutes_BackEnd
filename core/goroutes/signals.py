import json
import logging
import os
import re
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from core.goroutes.models import Route, PassengerRoute
from core.goroutes.utils.auto_route import otimizar_rotas_vans
from core.authentication.models import Passenger

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Route)
def set_start_address(sender, instance, **kwargs):
    if instance.auto_recalculate:
        logger.info("Iniciando cálculo automático de rota")
        try:
            # Coleta de endereços
            if not instance.addresses:
                passenger_ids = PassengerRoute.objects.filter(route=instance).values_list('passenger_id', flat=True)
                passengers = Passenger.objects.filter(id__in=passenger_ids).prefetch_related('address')

                if not passengers.exists():
                    logger.error("Nenhum passageiro encontrado para a rota")
                    return False

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
                raw_enderecos = instance.addresses
                addresses = [{"local": str(endereco), "passageiros": 1} for endereco in raw_enderecos if endereco]

                if not addresses:
                    logger.error("Lista de endereços explícitos está vazia")
                    return False

                logger.info(f"Usando {len(addresses)} endereços explícitos")

        except Exception as e:
            logger.error(f"Erro ao processar endereços: {e}")
            return False

        # Endereços inicial e final
        endereco_inicial = instance.origin
        endereco_final = instance.destination

        # Veículo
        if instance.vehicle:
            vans = [{
                "van": instance.vehicle.id,
                "lugares": instance.vehicle.seats,
                "endereco_inicial": endereco_inicial
            }]
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
                rota = rotas_otimizadas[0]
                instance.addresses_order = json.dumps(rota['caminho'], ensure_ascii=False)
                instance.distance = rota['distancia_total']
                instance.optimized_route_url = rota['link_maps']
                instance.coords_passageiros = rota.get('coords_passageiros', [])

                # Caminho do arquivo JSON salvo anteriormente
                json_path = os.path.join(settings.BASE_DIR, f"data_van_{instance.vehicle.id}.json")
                with open(json_path, 'r', encoding='utf-8') as f:
                    rota_json = json.load(f)

                # overview_polyline
                instance.overview_polyline = rota_json['routes'][0].get('overview_polyline', {})

                # Extrair steps e gerar markers + points
                steps = []
                points = []

                for leg in rota_json['routes'][0].get('legs', []):
                    for step in leg.get('steps', []):
                        clean_instruction = re.sub(r'<[^>]+>', '', step.get('html_instructions', ''))
                        steps.append({
                            "distance": step.get("distance", {}),
                            "duration": step.get("duration", {}),
                            "start_location": step.get("start_location", {}),
                            "end_location": step.get("end_location", {}),
                            "polyline": step.get("polyline", {}),
                            "html_instructions": clean_instruction
                        })

                        polyline_points = step.get("polyline", {}).get("points")
                        if polyline_points:
                            points.append(polyline_points)

                instance.markers = steps
                instance.points = points

                logger.info(f"Rota otimizada com sucesso: {len(rota['caminho'])} paradas")
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

    return True
