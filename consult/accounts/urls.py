from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signup_form/', views.signup_form, name='signup_form'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('resetpw/', views.resetpw, name='resetpw'),
    # path('send_email/', views.send_email, name = 'send_email'),
    path('password_reset/', views.UserPasswordResetView.as_view(), name="password_reset"),
    path('password_reset_done/', views.UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', views.UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    
    path('register/', views.register, name='register'),

]