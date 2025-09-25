from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.reverse import reverse

from core.goroutes.utils import ActivateRouteView, FilterDriverActiveRoutes, FilterDriverByIsActiveRoutes, FilterMyDriverRoutes, UpdateDocumentVehicle, UpdatePictureVehicle, RecalculateRoute, ChangePresenceStatusView, LocalJsonView,  CheckActiveDailyRouteDriverView
from core.goroutes.views import VehicleViewSet, NotifyViewSet, RouteViewSet, DailyRouteViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'notifies', NotifyViewSet, basename='notify')
router.register(r'routes', RouteViewSet, basename='routes')
router.register(r'dailyroute', DailyRouteViewSet, basename='dailyroute')


@api_view(['GET'])
def goroutes_root(request, format=None):
    return Response({
        'vehicles': reverse('vehicles-list', request=request, format=format),
        'notifies': reverse('notify-list', request=request, format=format),
        'routes': reverse('routes-list', request=request, format=format),
        'activate-route': reverse('activate-route', request=request, format=format),
        'filter-active-routes': reverse('filter-active-routes', request=request, format=format),
        'recalculate-route': reverse('recalculate-route', request=request, format=format),
        'daily-routes': reverse('dailyroute-list', request=request, format=format),
        "change-presence-status": reverse('change-presence-status', request=request, format=format),
        "show-jsons-create": reverse('show-jsons-create', request=format, format=format),
    })


urlpatterns = [
    path('', goroutes_root, name='goroutes-root'),
    path('', include(router.urls)),
    path('activate-route/', ActivateRouteView.as_view(), name='activate-route'),
    path('filter-active-routes/', FilterDriverActiveRoutes.as_view(), name='filter-active-routes'),
    path('recalculate-route/', RecalculateRoute.as_view(), name='recalculate-route'),
    path('filter-my-active-route/<int:driver_id>/', FilterDriverByIsActiveRoutes.as_view(), name='filter-my-active-route'),
    path('filter-my-driver-routes/<int:driver_id>/', FilterMyDriverRoutes.as_view(), name='filter-my-driver-routes'),
    path('update-document-vehicle/', UpdateDocumentVehicle.as_view(), name='update-document-vehicle'),
    path('update-picture-vehicle/', UpdatePictureVehicle.as_view(), name='update-picture-vehicle'),
    path('change-presence-status/', ChangePresenceStatusView.as_view(), name='change-presence-status'),
    path('show-jsons-create/', LocalJsonView.as_view(), name='show-jsons-create'),
    path('check-active-route-driver/<int:driver_id>/', CheckActiveDailyRouteDriverView.as_view(), name='check-active-route-driver'),
]
