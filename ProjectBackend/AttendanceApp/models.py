from django.db import models

# Create your models here.
class Teacher(models.Model):
    username = models.CharField(max_length = 20, unique= True)
    email = models.EmailField(max_length=40)
    password = models.CharField(max_length= 30)
    full_name = models.CharField(max_length=40)
    classes = models.CharField(max_length=10000)

class OneTimePassword(models.Model):
    email = models.EmailField(max_length = 40)
    otp = models.CharField(max_length = 6)
    time = models.CharField(max_length= 15)

class AttendanceRecord(models.Model):
    teacher_username = models.CharField(max_length= 20)
    class_name = models.CharField(max_length= 40) #this will be in the format o76bct051
    class_type = models.CharField(max_length = 20)
    subject = models.CharField(max_length = 40)
    date = models.DateField(auto_now = True)
    attendance_record = models.JSONField(max_length = 10000) #I expect a list here
    presence = models.FloatField()



    

