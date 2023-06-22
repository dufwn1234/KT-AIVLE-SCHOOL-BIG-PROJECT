from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.chat, name='chat'),
    #(0619 테스트용)########################
    path("test2/",views.test2,name='test2'),
    path("translater/",views.translater,name='translater'),
    path("test1/",views.test1,name='test1'),
    path("tanslater1/",views.translater1,name='translater1'),
    path("tanslater2/",views.translater2,name='translater2'),
    ########################################
    path("<str:room_name>/", views.room, name="room"),   
]
