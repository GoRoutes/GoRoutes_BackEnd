from django.contrib import admin
from core.authentication.models import User, Driver, Student, Parent

admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Student)
admin.site.register(Parent)

