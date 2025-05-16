from django.contrib import admin

from core.goroutes.models import LogEntry, Notify, Vehicle

admin.site.register(Vehicle)
admin.site.register(Notify)
admin.site.register(LogEntry)

# Register your models here.
