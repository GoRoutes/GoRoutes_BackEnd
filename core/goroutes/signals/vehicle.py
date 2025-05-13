from django.db.models.signals import post_save
from django.dispatch import receiver
from core.goroutes.models.vehicle import Vehicle
from core.goroutes.models.logentry import LogEntry
from core.authentication.middleware import get_current_user
from core.authentication.models import User

@receiver(post_save, sender=Vehicle)
def log_vehicle_save(sender, instance, created, **kwargs):
    user = get_current_user()
    print(f"user: {user}")
    action = 'create' if created else 'update'

    if not user or 'AnonymousUser' in str(user):
        userI = User.objects.get(pk=1)
        # supondo que o usuário de sistema tenha ID=1
        LogEntry.objects.create(
            user=userI,
            user_type='system',
            action=action,
            entity='Vehicle',
            entity_id=str(instance.id)
        )
    else:
        LogEntry.objects.create(
            user=user,
            user_type='user',
            action=action,
            entity='Vehicle',
            entity_id=str(instance.id)
        )