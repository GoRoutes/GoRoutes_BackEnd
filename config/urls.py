from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'authentication': reverse('authentication-root', request=request, format=format),
        # 'transport': reverse('transport-root', request=request, format=format),
        # 'uploader': reverse('uploader-root', request=request, format=format),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI 3
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
    # API
    path('api/', api_root, name='api-root'),
    path('api/authentication/', include('core.authentication.urls')),
    # path('api/transport/', include('core.transport.urls')),
    # path('api/uploader/', include('core.uploader.urls')),
    path('', lambda request: redirect('api/', permanent=True)),
]
