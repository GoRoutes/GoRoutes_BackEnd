from django.db import models
from django.utils.translation import gettext_lazy as _

from core.authentication.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    grade = models.CharField(max_length=255, help_text=_("The grade of the student"), null=True, blank=True)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self):
        return self.user.email
