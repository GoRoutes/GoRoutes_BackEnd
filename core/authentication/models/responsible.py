from django.db import models
from core.authentication.models import User, Passenger

class Responsible(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='responsible')
    cpf = models.CharField(max_length=11, unique=True)
    students = models.ManyToManyField(Passenger, related_name='responsibles')
    kinship = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.cpf}'