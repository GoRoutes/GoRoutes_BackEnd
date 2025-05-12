from django.db import models
from django.utils.translation import gettext_lazy as _


class VehicleStatus(models.TextChoices):
    MAINTENANCE = 'manutenção'
    AVAILABLE = 'disponível'
    ON_ROUTE = 'em rota'


class Vehicle(models.Model):
    plate = models.CharField(max_length=255, help_text=_("The plate of the vehicle"))
    model = models.CharField(max_length=255, help_text=_("The model of the vehicle"))
    seats = models.IntegerField(help_text=_("The number of seats of the vehicle"))
    picture = models.ImageField(upload_to='vehicles/', help_text=_("The picture of the vehicle"))
    status = models.CharField(max_length=255, choices=VehicleStatus.choices, help_text=_("The status of the vehicle"))

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return self.plate