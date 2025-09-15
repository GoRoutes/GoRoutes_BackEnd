from django.db import models
from django.utils.translation import gettext_lazy as _
from core.uploader.models import Image, Document


class VehicleStatus(models.TextChoices):
    MAINTENANCE = "manutenção"
    AVAILABLE = "disponível"
    ON_ROUTE = "em rota"


class Vehicle(models.Model):
    plate = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    seats = models.IntegerField()
    status = models.CharField(max_length=255, choices=VehicleStatus.choices)
    picture = models.OneToOneField(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_picture",
    )
    CRLV = models.OneToOneField(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_crlv",
    )
    CV = models.OneToOneField(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_cv",
    )
    AD = models.OneToOneField(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_ad",
    )
    

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return self.plate
