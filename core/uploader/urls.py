from django.urls import include, path, reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, status

from core.uploader.views import ImagesViewSet, DocumentsViewSet, DownloadDocumentView

router = DefaultRouter()

router.register(r'images', ImagesViewSet, basename='images')
router.register(r'documents', DocumentsViewSet, basename='documents')

@api_view(['GET'])
def uploader_root(request, format=None):
    return Response({
        'images': reverse('images-list', request=request, format=format),
        'documents': reverse('documents-list', request=request, format=format),
    })

urlpatterns = [
    path('', uploader_root, name='uploader-root'),
    path('', include(router.urls)),
    path("download/<path:public_id>/", DownloadDocumentView.as_view(), name="download-document"),
]
