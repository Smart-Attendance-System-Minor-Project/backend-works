from django.db import models

# Create your models here.
class Teacher(models.Model):
    username = models.CharField(max_length = 20, unique= True)
    email = models.EmailField(max_length=40)
    password = models.CharField(max_length= 30)
    full_name = models.CharField(max_length=40)
    classes = models.CharField(max_length=1000)
    

