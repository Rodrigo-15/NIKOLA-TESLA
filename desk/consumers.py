import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import datetime


class DeskSocket(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        # self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_add)(self.user_id, self.channel_name)
        self.accept()
        print("connected")

    def disconnect(self, close_code):
        print("Disconnected")
        async_to_sync(self.channel_layer.group_discard)(self.user_id, self.channel_name)
        pass

    def receive(self, text_data):
        print("Received")
        pass

    def desk_notification(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))
        pass
