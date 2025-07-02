from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.reverse import reverse

from core.goroutes.views import VehicleViewSet, NotifyViewSet, RouteViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'notifies', NotifyViewSet, basename='notify')
router.register(r'routes', RouteViewSet, basename='routes')

@api_view(['GET'])
def goroutes_root(request, format=None):
    return Response({
        'vehicles': reverse('vehicles-list', request=request, format=format),
        'notifies': reverse('notify-list', request=request, format=format),
        'routes': reverse('routes-list', request=request, format=format),
    })

urlpatterns = [
    path('', goroutes_root, name='goroutes-root'),
    path('', include(router.urls)),
]
