from django.apps import AppConfig


class GoroutesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.goroutes'

    def ready(self):
        import core.goroutes.signals.vehicle
    