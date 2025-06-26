from rest_framework.routers import DefaultRouter


from core.uploader.views import ImageViewSet

uploader_router = DefaultRouter()
uploader_router.register(r'images', ImageViewSet)