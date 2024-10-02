import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync


class DeskSocket(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        await self.channel_layer.group_add(self.user_id, self.channel_name)
        await self.accept()
        print("Conexión establecida")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_id, self.channel_name)
        print("Desconectado")

    async def receive(self, text_data):
        pass

    async def desk_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
