from django.urls import include, path, reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, status

from core.authentication.views.infra import UserViewSet, DriverViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'drivers', DriverViewSet, basename='driver')

@api_view(['GET'])
def authentication_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'drivers': reverse('driver-list', request=request, format=format),
    })

urlpatterns = [
    path('', authentication_root, name='authentication-root'),
    path('', include(router.urls)),
]
