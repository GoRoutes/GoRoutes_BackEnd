from django.contrib import admin
from core.goroutes.models import Route, PassengerRoute, Vehicle, DailyRoute, DataCacheRoute
from core.authentication.models import Passenger

class PassengerRouteInline(admin.TabularInline):
    model = PassengerRoute
    extra = 1
    autocomplete_fields = ['passenger']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin', 'destination', 'vehicle']
    inlines = [PassengerRouteInline]

@admin.register(DataCacheRoute)
class DataCacheRouteAdmin(admin.ModelAdmin):
    list_display = [
        'origin_truncated', 
        'destination_truncated', 
        'distance', 
        'duration', 
        'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = [
        'origin',
        'destination', 
        'latitude_origin',
        'longitude_origin',
        'latitude_destination', 
        'longitude_destination'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    def origin_truncated(self, obj):
        return obj.origin[:50] + '...' if len(obj.origin) > 50 else obj.origin
    origin_truncated.short_description = 'Origem'
    
    def destination_truncated(self, obj):
        return obj.destination[:50] + '...' if len(obj.destination) > 50 else obj.destination
    destination_truncated.short_description = 'Destino'
    
    fieldsets = (
        ('Informações da Rota', {
            'fields': ('origin', 'destination', 'polyline')
        }),
        ('Distância e Duração', {
            'fields': ('distance', 'duration')
        }),
        ('Coordenadas de Origem', {
            'fields': ('latitude_origin', 'longitude_origin')
        }),
        ('Coordenadas de Destino', {
            'fields': ('latitude_destination', 'longitude_destination')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(PassengerRoute)
admin.site.register(Vehicle)
admin.site.register(DailyRoute)