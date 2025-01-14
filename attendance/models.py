from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()


class AttendanceSession(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    lecturer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conducted_sessions'  # Changed from courses_taught
    )
    qr_code = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.course} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
        ('EXCUSED', 'Excused'),
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    location_data = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRESENT'
    )

    class Meta:
        ordering = ['-timestamp']
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"
