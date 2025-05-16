from django.contrib import admin

from core.authentication.models import Driver, Parent, Student, User

admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Student)
admin.site.register(Parent)
