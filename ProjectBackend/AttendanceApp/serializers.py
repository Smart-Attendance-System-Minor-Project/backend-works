from rest_framework.serializers import ModelSerializer as msz
from .models import AttendanceRecord

class RecordSerializer(msz):
    class Meta:
        model = AttendanceRecord
        fields = ['teacher_username', 'class_name', 'class_type', 'subject', 'attendance_record']
