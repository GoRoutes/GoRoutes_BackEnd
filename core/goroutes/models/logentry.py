from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class LogEntry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='goroutes_log_entries'   # <— aqui
    )
    user_type = models.CharField(max_length=10)
    action = models.CharField(max_length=10)
    entity = models.CharField(max_length=10)
    entity_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} – {self.action} – {self.entity} – {self.entity_id}"
