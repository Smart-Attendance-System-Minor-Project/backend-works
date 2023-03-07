from django.contrib import admin
from .models import Teacher, AttendanceRecord
from django.contrib.auth.admin import UserAdmin
# Register your models here.
@admin.register(Teacher)
class Teacher(admin.ModelAdmin):
    list_display = ['username', 'email']

# admin.site.register(Teacher)

@admin.register(AttendanceRecord)
class AttendanceRecord(admin.ModelAdmin):
    list_display = ['teacher_username', 'class_name', 'class_type', 'subject', 'attendance_record']
