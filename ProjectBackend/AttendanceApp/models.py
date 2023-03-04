from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,AbstractUser
from .managers import TeacherManager

# Create your models here.
class Teacher(AbstractUser):
    username = models.CharField(max_length = 20, unique= True)
    email = models.EmailField(max_length=40, unique=True)
    # password = models.CharField(max_length= 30)
    full_name = models.CharField(max_length=40)
    classes = models.CharField(max_length= 10000)

    USERNAME_FIELD = 'username'
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # is_admin = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['full_name', 'email']

    objects = TeacherManager()

    def has_perm(self,perm,obj=None):
        return self.is_staff

    def has_module_perms(self,app_label):
        return True


class OneTimePassword(models.Model):
    email = models.EmailField(max_length = 40)
    otp = models.CharField(max_length = 6)
    time = models.CharField(max_length= 15)

class AttendanceRecord(models.Model):
    teacher_username = models.CharField(max_length= 20)
    class_name = models.CharField(max_length= 40) #this will be in the format o76bctab
    class_type = models.CharField(max_length = 20)
    subject = models.CharField(max_length = 40)
    attendance_record = models.JSONField() 
    



    

