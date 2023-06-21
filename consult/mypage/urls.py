from django.urls import path
from . import views

app_name = 'mypage'
urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('update/', views.update, name='update'),
    path('chatdetail/<cpk>', views.chatdetail, name='chatdetail'),
    path('calldetail/<cpk>', views.calldetail, name='calldetail'),
    path('delete/', views.delete, name='delete'),
    path('img_update/', views.img_update, name='img_update'),
    path('img_delete/', views.img_delete, name='img_delete'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
