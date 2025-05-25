from django.contrib import admin
from core.authentication.models import Address, User, Driver, Passenger, StudentData, Responsible

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Driver)
admin.site.register(Passenger)
admin.site.register(StudentData)
admin.site.register(Responsible)