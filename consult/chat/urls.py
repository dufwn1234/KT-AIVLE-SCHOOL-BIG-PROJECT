from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.chat, name='chat'),
    path('chat_end/', views.chat_end, name="chat_end"),
    path("<str:room_name>/", views.room, name="room"),  
]
