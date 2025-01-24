# attendance/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from courses.models import Course, CourseCategory
from .models import AttendanceSession, Attendance

User = get_user_model()


class AttendanceTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='teacherpass',
            is_staff=True
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='studentpass'
        )

        self.category = CourseCategory.objects.create(name='Test Category')
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            category=self.category,
            instructor=self.teacher,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            max_students=30,
            credits=3.0
        )

        self.client = APIClient()

    def test_create_attendance_session(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post('/api/attendance/sessions/', {
            'course': self.course.id,
            'is_geofencing_enabled': True,
            'allowed_latitude': 3.1390,
            'allowed_longitude': 101.6869,
            'geofence_radius': 50
        })

        self.assertEqual(response.status_code, 201)
        self.assertTrue('qr_code' in response.data)

    def test_student_checkin(self):
        session = AttendanceSession.objects.create(
            course=self.course,
            is_geofencing_enabled=True,
            allowed_latitude=3.1390,
            allowed_longitude=101.6869
        )

        self.client.force_authenticate(user=self.student)

        # Check-in with valid location
        response = self.client.post(f'/api/attendance/sessions/{session.id}/check_in/', {
            'latitude': 3.1390,
            'longitude': 101.6869
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Attendance.objects.filter(student=self.student, session=session).exists())

    def test_invalid_location_checkin(self):
        session = AttendanceSession.objects.create(
            course=self.course,
            is_geofencing_enabled=True,
            allowed_latitude=3.1390,
            allowed_longitude=101.6869,
            geofence_radius=50
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.post(f'/api/attendance/sessions/{session.id}/check_in/', {
            'latitude': 4.0,
            'longitude': 102.0
        })

        self.assertEqual(response.status_code, 403)

    def test_attendance_percentage(self):
        sessions = [
            AttendanceSession.objects.create(course=self.course) for _ in range(5)
        ]

        for session in sessions[:3]:
            Attendance.objects.create(student=self.student, session=session)

        self.client.force_authenticate(user=self.student)

        response = self.client.get(f'/api/attendance/records/attendance_percentage/?course_id={self.course.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_sessions'], 5)
        self.assertEqual(response.data['attended_sessions'], 3)
        self.assertEqual(response.data['attendance_percentage'], 60)

    def test_terminate_session(self):
        self.client.force_authenticate(user=self.teacher)

        session = AttendanceSession.objects.create(
            course=self.course,
            is_active=True
        )

        response = self.client.post(f'/api/attendance/sessions/{session.id}/terminate/')

        self.assertEqual(response.status_code, 200)

        session.refresh_from_db()
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.end_time)
