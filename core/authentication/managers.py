from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password, name, **extra_fields):
        
        if not email:
            raise ValueError("The given email must be set")  
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, name, password, **extra_fields):
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        super_user_name = "admin"

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        user = self.model(email=email, name=name, password=password)
        return self.create_user(email = user.email, name=user.name, password = user.password, **extra_fields)
    