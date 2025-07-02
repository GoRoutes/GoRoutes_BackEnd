from django.db import models

class Route(models.Model):
    name = models.CharField(max_length=255, unique=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance = models.FloatField()
    init_hour = models.TimeField()
    end_hour = models.TimeField()
    duration = models.FloatField()
    latitude_origin = models.FloatField()
    longitude_origin = models.FloatField()
    latitude_destination = models.FloatField()
    longitude_destination = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route from {self.origin} to {self.destination} ({self.distance} km)"
    
    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        ordering = ['created_at']