from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'athletes', AthleteViewSet)
# router.register(r'personals', PersonalViewSet)
# router.register(r'users', UserViewSet)
# router.register(r'drivers', DriverViewSet)
# router.register(r'students', StudentViewSet)


@api_view(['GET'])
def authentication_root(request, format=None):
    return Response({
        # 'athletes': reverse('athlete-list', request=request, format=format),
        # 'personals': reverse('personal-list', request=request, format=format),
        # 'users': reverse('user-list', request=request, format=format),
        # 'drivers': reverse('driver-list', request=request, format=format),
        # 'students': reverse('student-list', request=request, format=format),
    })


urlpatterns = [
    path('', authentication_root, name='authentication-root'),
    path('', include(router.urls)),
]
