from django.contrib import admin
from .models import Teacher, AttendanceRecord
# Register your models here.
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

@admin.register(AttendanceRecord)
class AttendanceRecord(admin.ModelAdmin):
    list_display = ['teacher_username', 'class_name', 'class_type', 'subject', 'date', 'attendance_record', 'presence']
