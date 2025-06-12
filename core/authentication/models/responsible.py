from django.db import models
from core.authentication.models import User

class Responsible(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='responsible')
    cpf = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return f'{self.user.username} - {self.cpf}'