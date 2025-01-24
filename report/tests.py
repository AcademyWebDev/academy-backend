from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from grades.models import Assessment, Grade
from django.contrib.auth import get_user_model
from courses.models import Course, CourseCategory
from attendance.models import AttendanceSession, Attendance
from .models import StudentPerformanceReport, CoursePerformanceReport

User = get_user_model()


class ReportTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='teacherpass'
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

        self.assessment1 = Assessment.objects.create(
            course=self.course,
            date=timezone.now().date(),
            title='Test Assessment 1',
            max_score=100,
            weight=0.5
        )
        self.assessment2 = Assessment.objects.create(
            course=self.course,
            date=timezone.now().date(),
            title='Test Assessment 2',
            max_score=100,
            weight=0.5
        )

        Grade.objects.create(
            student=self.student,
            assessment=self.assessment1,
            score=80
        )
        Grade.objects.create(
            student=self.student,
            assessment=self.assessment2,
            score=90
        )

        self.attendance_sessions = [
            AttendanceSession.objects.create(course=self.course) for _ in range(5)
        ]

        for session in self.attendance_sessions[:3]:
            Attendance.objects.create(student=self.student, session=session)

        self.client = APIClient()

    def test_student_performance_report_generation(self):
        report = StudentPerformanceReport.generate_report(self.student, self.course)

        self.assertEqual(report.total_assessments, 2)
        self.assertAlmostEqual(report.average_grade, 85)
        self.assertAlmostEqual(report.attendance_percentage, 60)

    def test_course_performance_report_generation(self):

        report = CoursePerformanceReport.generate_report(self.course)

        self.assertEqual(report.total_students, 1)
        self.assertAlmostEqual(report.average_course_grade, 85)
        self.assertAlmostEqual(report.overall_attendance_rate, 60)

    def test_student_performance_report_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        StudentPerformanceReport.generate_report(course=self.course, student=self.student)

        response = self.client.get(f'/api/reports/student_performance/?course_id={self.course.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertAlmostEqual(float(response.data[0]['average_grade']), 85)

    def test_course_performance_report_endpoint(self):
        CoursePerformanceReport.generate_report(self.course)

        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/reports/course_performance/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertAlmostEqual(float(response.data[0]['average_course_grade']), 85)

    def test_non_admin_access(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get('/api/reports/course_performance/')

        self.assertEqual(response.status_code, 403)

    def test_student_performance_single_student(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.get(f'/api/reports/student_performance/?course_id={self.course.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertAlmostEqual(response.data[0]['average_grade'], 85)
