from django.contrib import admin
from core.authentication.models import Address, User, Driver

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Driver)