from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('user/', views.helloUser),
    path('register/', views.teacherRegistration),
    path('login/', views.login),
    path('forgot_password/', views.forgotPassword),
    path('otp_validation/', views.validateOTP)
    
]