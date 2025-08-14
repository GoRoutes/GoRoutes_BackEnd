from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.reverse import reverse

from core.goroutes.views import VehicleViewSet, NotifyViewSet, RouteViewSet
from core.goroutes.utils import ActivateRouteView, FilterDriverByIsActiveRoutes, FilterDriverByIsActiveRoutes

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'notifies', NotifyViewSet, basename='notify')
router.register(r'routes', RouteViewSet, basename='routes')


@api_view(['GET'])
def goroutes_root(request, format=None):
    """
    Retorna URLs genéricas para recursos que não dependem de driver_id.
    URLs que precisam de driver_id devem ser chamadas diretamente.
    """
    return Response({
        'vehicles': reverse('vehicles-list', request=request, format=format),
        'notifies': reverse('notify-list', request=request, format=format),
        'routes': reverse('routes-list', request=request, format=format),
        'activate-route': reverse('activate-route', request=request, format=format),
        'filter-active-routes': reverse('filter-active-routes', request=request, format=format),
        # 'filter-my-active-route' não é gerado aqui, pois precisa de driver_id
    })


urlpatterns = [
    path('', goroutes_root, name='goroutes-root'),
    path('', include(router.urls)),
    path('activate-route/', ActivateRouteView.as_view(), name='activate-route'),
    path('filter-active-routes/', FilterDriverByIsActiveRoutes.as_view(), name='filter-active-routes'),
    path('filter-my-active-route/<int:driver_id>/', FilterDriverByIsActiveRoutes.as_view(), name='filter-my-active-route'),
]
