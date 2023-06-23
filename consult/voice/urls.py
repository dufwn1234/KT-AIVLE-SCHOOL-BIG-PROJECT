from django.urls import path
from . import views

app_name = 'voice'
urlpatterns = [
    path('', views.test, name='test'),
    path('voicetest/', views.test1, name='test1'),
    path('counselor/', views.counselor, name='counselor'),
    path('account/', views.account, name='account'),
    path('summary/', views.summary, name='summary'),
    path('history/', views.history, name='history'),
    path('client/', views.client, name='client'),
    path('voice_en/', views.voice_en, name='voice_en'),
    path('voice_ja/', views.voice_ja, name='voice_ja'),
    path('voice_ch/', views.voice_ch, name='voice_ch'),
    path('voice_vi/', views.voice_vi, name='voice_vi'),
    path('voice_th/', views.voice_th, name='voice_th'),
    path('stttest/', views.stttest, name='stttest'),
    path('apitest/', views.apitest, name='apitest'),
    path('tts/', views.tts, name='tts'),
    # path('summary/', views.summary, name='summary'),
    
]