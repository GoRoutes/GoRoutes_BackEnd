from django.contrib.auth.models import AbstractUser
from django.db import models
from core.authentication.managers import CustomUserManager

class User(AbstractUser):
    username = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, null=False, blank=False)
    passage_id = models.CharField(max_length=255, null=False, blank=False)
    data_of_birth = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    EMAIL_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'