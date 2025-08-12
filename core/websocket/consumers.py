# core/websocket/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from core.goroutes.utils.update_mylocation import update_mylocation

class LocalizacaoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        await update_mylocation(data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'enviar_localizacao',
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }
        )

    async def enviar_localizacao(self, event):
        await self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
