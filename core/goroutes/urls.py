from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.reverse import reverse

from core.goroutes.views import VehicleViewSet, NotifyViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicles')
router.register(r'notifies', NotifyViewSet, basename='notify')
# router.register(r'athletes', AthleteViewSet)
# router.register(r'personals', PersonalViewSet)
# router.register(r'users', UserViewSet)
# router.register(r'drivers', DriverViewSet)
# router.register(r'students', StudentViewSet)


@api_view(['GET'])
def goroutes_root(request, format=None):
    return Response({
        'vehicles': reverse('vehicles-list', request=request, format=format),
        'notifies': reverse('notify-list', request=request, format=format),
        # 'athletes': reverse('athlete-list', request=request, format=format),
        # 'personals': reverse('personal-list', request=request, format=format),
        # 'users': reverse('user-list', request=request, format=format),
        # 'drivers': reverse('driver-list', request=request, format=format),
        # 'students': reverse('student-list', request=request, format=format),
    })


urlpatterns = [
    path('', goroutes_root, name='goroutes-root'),
    path('', include(router.urls)),
]
