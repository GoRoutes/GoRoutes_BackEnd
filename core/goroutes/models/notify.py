from django.db import models
from django.utils.translation import gettext_lazy as _


class NotifyType(models.TextChoices):
    Parents = 'responsaveis'
    Parent = 'responsavel'
    Students = 'alunos'
    Student = 'aluno'
    Drivers = 'motoristas'
    Driver = 'motorista'
    Admins = 'administradores'


class Notify(models.Model):
    tipo = models.CharField(max_length=255, help_text=_("The type of the notify"))
    message = models.TextField(help_text=_("The message of the notify"))
    to_type = models.CharField(max_length=255, choices=NotifyType.choices, help_text=_("The type of the notify"))
    to_id = models.IntegerField(help_text=_("The id of the notify"))
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("The created at of the notify"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("The updated at of the notify"))

    class Meta:
        verbose_name = _("Notify")
        verbose_name_plural = _("Notifies")