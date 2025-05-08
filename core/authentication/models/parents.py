from django.db import models
from core.authentication.models import User, Student
from django.utils.translation import gettext_lazy as _

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent')
    document_number = models.CharField(max_length=255, help_text=_("The number of the parent"), null=True, blank=True)
    children = models.ManyToManyField(Student, related_name='parents', help_text=_("The children of the parent"))

    class Meta:
        verbose_name = _("Parent")
        verbose_name_plural = _("Parents")

    def __str__(self):
        return self.user.email