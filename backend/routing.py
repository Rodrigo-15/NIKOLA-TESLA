from django.urls import path
from desk.consumers import DeskSocket

websocket_urlpatterns = [
    path("ws/desk/", DeskSocket.as_asgi()),
]
