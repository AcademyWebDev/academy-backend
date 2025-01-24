import uuid
from django.db import models
from geopy.distance import geodesic
from accounts.models import User
from django.utils import timezone
from courses.models import Course


class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qr_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    is_geofencing_enabled = models.BooleanField(default=False)
    allowed_latitude = models.FloatField(null=True, blank=True)
    allowed_longitude = models.FloatField(null=True, blank=True)
    geofence_radius = models.FloatField(default=50)  # meters

    is_active = models.BooleanField(default=True)

    def terminate_session(self):
        self.is_active = False
        self.end_time = timezone.now()
        self.save()

    def is_valid_location(self, latitude, longitude):
        if not self.is_geofencing_enabled:
            return True

        campus_location = (self.allowed_latitude, self.allowed_longitude)
        student_location = (latitude, longitude)

        distance = geodesic(campus_location, student_location).meters
        return distance <= self.geofence_radius


class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('late', 'Late'),
            ('absent', 'Absent')
        ],
        default='present'
    )