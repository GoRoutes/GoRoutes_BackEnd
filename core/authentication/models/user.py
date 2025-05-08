from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    name = models.CharField(max_length=255, help_text=_("The name of the user"))
    email = models.EmailField(max_length=255, unique=True, help_text=_("The email of the user"))
    password = models.CharField(max_length=255, help_text=_("The password of the user"))
    is_active = models.BooleanField(default=True, help_text=_("Whether the user is active"))
    is_staff = models.BooleanField(default=False, help_text=_("Whether the user is staff"))
    # picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, help_text=_("The profile picture of the user"))
    phone = models.CharField(max_length=255, null=True, blank=True, help_text=_("The phone number of the user"))
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    
    
    def save(self, *args, **kwargs):
        if self.pk and not self._state.adding and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")