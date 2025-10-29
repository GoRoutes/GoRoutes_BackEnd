from django.db import models
from .normalize_text import normalizar_texto

try:
    from core.authentication.models import Address
except ImportError:
    pass

def salvar_coordenadas_no_cache(endereco: str, lat: float, lng: float):
    """
    Salva coordenadas no Address para cache futuro
    """
    try:
        partes = endereco.split(',')
        rua_numero = partes[0].strip() if partes else endereco
        bairro = partes[1].strip() if len(partes) > 1 else "Desconhecido"
        
        rua_partes = rua_numero.split(' ')
        numero = None
        rua_sem_numero = rua_numero
        
        for i in range(len(rua_partes)-1, -1, -1):
            if rua_partes[i].replace('.', '').isdigit():
                numero = rua_partes[i]
                rua_sem_numero = ' '.join(rua_partes[:i])
                break
        
        rua_sem_numero_normalizada = normalizar_texto(rua_sem_numero)
        bairro_normalizado = normalizar_texto(bairro)
        
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
            address.latitude = str(lat)
            address.longitude = str(lng)
            address.save()
            print(f"💾 Coordenadas atualizadas no cache: {endereco}")
            
    except Exception as e:
        print(f"⚠️ Não foi possível salvar no cache: {e}")