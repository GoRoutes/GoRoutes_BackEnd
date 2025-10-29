from celery import shared_task
from core.goroutes.models import DataCacheRoute

@shared_task(bind=True, max_retries=3)
def clear_cache_table(self):
    """
    Limpa TODA a tabela de cache (remove todos os registros)
    """
    try:
        total_registros = DataCacheRoute.objects.count()
        
        DataCacheRoute.objects.all().delete()
        
        return {
            'status': 'success',
            'message': f'Tabela de cache limpa completamente',
            'registros_removidos': total_registros
        }
        
    except Exception as e:
        self.retry(countdown=300, exc=e)