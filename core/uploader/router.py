from rest_framework.routers import DefaultRouter


from core.uploader.views import ImageViewSet
from core.uploader.views import DocumentsViewSet

uploader_router = DefaultRouter()
uploader_router.register(r'images', ImageViewSet)
uploader_router.register(r'documents', DocumentsViewSet)