
from django.db import models
from core.authentication.models import User, Address

class Driver(models.Model):
    cnh = models.CharField(max_length=20, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    cpf = models.CharField(max_length=14, null=False, blank=False)
    adresses = models.ManyToManyField(Address, related_name='drivers', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')

    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'