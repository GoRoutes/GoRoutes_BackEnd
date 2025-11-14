from django.db import models
from core.goroutes.models import Route, Vehicle
from core.authentication.models import Driver, Passenger

class DailyRoute(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='daily_routes')
    init_hour = models.TimeField()
    end_hour = models.TimeField()
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='daily_routes', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='daily_routes', null=True, blank=True)
    latitude_origin = models.FloatField()
    longitude_origin = models.FloatField()
    latitude_destination = models.FloatField()
    longitude_destination = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    auto_recalculate = models.BooleanField(default=False)
    addresses = models.JSONField(default=list)
    optimized_route_url = models.TextField(null=True, blank=True)
    overview_polyline = models.JSONField(null=True, blank=True)
    markers = models.JSONField(null=True, blank=True)
    coords_passageiros = models.JSONField(default=list)
    points = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    original = models.BooleanField()
    finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"
    
    class Meta:
        verbose_name = 'Daily Route'
        verbose_name_plural = 'Daily Routes'
        ordering = ['-date', 'init_hour']

class Presence(models.Model):
    class Status(models.TextChoices):
        PRESENTE = 'PRESENTE', 'Present'
        FALTOU = 'FALTOU', 'FALTOU'
        NAO_PEGO = 'NAO_PEGO', 'NAO_PEGO'

    daily_route = models.ForeignKey(DailyRoute, on_delete=models.CASCADE, related_name='presences')
    passenger_route = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='presences')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NAO_PEGO)

    def __str__(self):
        return f"Presence of {self.passenger_route.user.name} on {self.daily_route.name} - {self.daily_route.date}"
    
    class Meta:
        verbose_name = 'Presence'
        verbose_name_plural = 'Presences'
        unique_together = ('daily_route', 'passenger_route')