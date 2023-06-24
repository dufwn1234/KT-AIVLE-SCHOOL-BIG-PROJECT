from django.urls import path
from . import views

app_name = 'voicechat'
urlpatterns = [
    path('', views.voicechat, name='voicechat'),  
    path('stt/', views.stt, name='stt'),
    path("<str:room_name>/", views.room, name="room"), 
]