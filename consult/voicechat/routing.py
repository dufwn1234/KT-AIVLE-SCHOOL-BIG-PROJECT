from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/voicetalk/(?P<room_name>\w+)/$", consumers.VoiceChatConsumer.as_asgi()),
]