from django.contrib import admin

from core.goroutes.models import Route, PassengerRoute

admin.site.register(Route)
admin.site.register(PassengerRoute)