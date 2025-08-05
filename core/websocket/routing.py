from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/localizacao/(?P<motorista_id>\w+)/$', consumers.LocalizacaoConsumer.as_asgi()),
]
