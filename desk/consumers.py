import json
from channels.generic.websocket import WebsocketConsumer


class DeskSocket(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("Connected")

    def disconnect(self, close_code):
        print("Disconnected")
        pass

    def receive(self, text_data):

        print("Received")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            self.send(text_data=json.dumps({"message": message}))
        except json.decoder.JSONDecodeError as e:
            print("Error decoding JSON")
            pass
