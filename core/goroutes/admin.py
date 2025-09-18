from django.contrib import admin
from core.goroutes.models import Route, PassengerRoute, Vehicle, DailyRoute
from core.authentication.models import Passenger

class PassengerRouteInline(admin.TabularInline):
    model = PassengerRoute
    extra = 1
    autocomplete_fields = ['passenger']

# Admin para a rota com o inline de passageiros
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin', 'destination', 'vehicle']
    inlines = [PassengerRouteInline]

admin.site.register(PassengerRoute)
admin.site.register(Vehicle)
admin.site.register(DailyRoute)