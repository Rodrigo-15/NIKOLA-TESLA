from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("connected")

    async def disconnect(self, close_code):
        print("disconnected", close_code)
        pass

    async def receive(self, text_data):
        print("receive", text_data)
