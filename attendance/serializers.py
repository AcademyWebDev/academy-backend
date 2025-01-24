from rest_framework import serializers
from .models import AttendanceSession, Attendance


class AttendanceSessionSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'course', 'qr_code',
            'start_time', 'end_time',
            'is_geofencing_enabled',
            'allowed_latitude',
            'allowed_longitude',
            'geofence_radius',
            'is_active'
        ]

    def get_qr_code(self, obj):
        return str(obj.qr_code)


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['student', 'session', 'check_in_time', 'latitude', 'longitude', 'status']
