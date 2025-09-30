# yourapp/models.py
from django.db import models

class DataCacheRoute(models.Model):
    origin = models.TextField()
    destination = models.TextField()
    distance  = models.IntegerField()
    duration = models.IntegerField()
    polyline = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    latitude_origin = models.CharField(max_length=30)
    longitude_origin = models.CharField(max_length=30)
    latitude_destination = models.CharField(max_length=30)
    longitude_destination = models.CharField(max_length=30)
    
    
    class Meta:
        db_table = 'rotas_cache'
        unique_together = ['origin', 'destination']
        
    def __str__(self):
        return f"{self.origin} -> {self.destination}"