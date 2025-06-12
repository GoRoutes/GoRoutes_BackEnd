from django.db import models
from core.authentication.models import User
from django.utils.translation import gettext_lazy as _

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    cnh = models.CharField(max_length=255, help_text=_("The CNH of the driver"), null=True, blank=True)
    active = models.BooleanField(default=True, help_text=_("Whether the driver is active"))
    

    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")




