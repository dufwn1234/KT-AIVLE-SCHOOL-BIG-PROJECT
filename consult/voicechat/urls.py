from django.urls import path
from . import views

app_name = 'voicetalk'
urlpatterns = [
    path('', views.voicechat, name='voicechat'),  
    path('voicetalk_end/', views.voicechat_end, name="voicechat_end"),
    path("<str:room_name>/", views.room, name="room"), 
    path('test/', views.calldraft, name='test'),
    path('sum', views.sum, name='sum'),
    path('summ', views.summ, name='summ'),  
    path('test', views.calldraft, name='calldraft'),  
]