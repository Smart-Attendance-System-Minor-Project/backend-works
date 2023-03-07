from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('user/', views.helloUser),
    path('register/', views.teacherRegistration),
    path('login/', views.login),
    path('forgot_password/', views.forgotPassword),
    path('otp_validation/', views.validateOTP), 
    path('password_reset/', views.passwordReset),
    path('teachers/', views.seeUsers),
    path('add_class/', views.addClass),
    path('view_class/', views.viewClasses),
    path('view_otps/', views.viewOTP),
    path('save_record/', views.saveRecord),
    path('get_records/', views.getRecords),
    path('create_user/', views.createUser),
    path('warn/', views.warnStudents),
    path('recent_date/', views.returnRecentDate),
    
]