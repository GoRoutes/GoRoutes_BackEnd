from django.contrib import admin
from core.goroutes.models import Vehicle, Notify, LogEntry

admin.site.register(Vehicle)
admin.site.register(Notify)
admin.site.register(LogEntry)

# Register your models here.
