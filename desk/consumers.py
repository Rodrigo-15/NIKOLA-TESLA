import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import datetime


class DeskSocket(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_add)(self.user_id, self.channel_name)
        self.accept()
        print("user_id: ", self.user_id)

    def disconnect(self, close_code):
        print("Disconnected")
        async_to_sync(self.channel_layer.group_discard)(self.user_id, self.channel_name)
        pass

    def receive(self, text_data):
        print("Received", text_data)
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            if self.scope["user"].is_authenticated:
                sender_id = self.scope["user"].id
            else:
                None

            if sender_id:
                async_to_sync(self.channel_layer.group_send)(
                    self.user_id,
                    {
                        "type": "chat_message",
                        "message": message,
                        "username": self.user.username,
                        "datetime": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    },
                )
            else:
                print("User not authenticated")

        except json.JSONDecodeError as e:
            print("Error decoding JSON", e)
            pass
        except KeyError as e:
            print("Clave no encontrada", e)
            pass
        except Exception as e:
            print("Error: ", e)
            pass

    def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        datetime = event["datetime"]
        sender_id = event["sender_id"]

        current_user_id = self.scope["user"].id
        if sender_id != current_user_id:
            self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "username": username,
                        "datetime": datetime,
                    }
                )
            )
