from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from courses.models import Course, CourseCategory
from .models import Assessment, Grade

User = get_user_model()


class GradesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

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

        self.assessment = Assessment.objects.create(
            course=self.course,
            title='Midterm Exam',
            assessment_type='midterm',
            max_score=100,
            weight=50,
            date=timezone.now().date()
        )

    def test_create_assessment(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/grades/assessments/', {
            'course': self.course.id,
            'title': 'Final Exam',
            'assessment_type': 'final',
            'max_score': 100,
            'weight': 50,
            'date': timezone.now().date()
        })
        self.assertEqual(response.status_code, 201)

    def test_record_grade(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/grades/records/', {
            'student': self.student.id,
            'assessment': self.assessment.id,
            'score': 85
        })
        self.assertEqual(response.status_code, 201)

    def test_student_view_grades(self):
        Grade.objects.create(
            student=self.student,
            assessment=self.assessment,
            score=85
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/grades/records/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(int(response.data[0]['score'].split('.')[0]), 85)

    def test_course_performance(self):
        assessment2 = Assessment.objects.create(
            course=self.course,
            title='Assignment',
            assessment_type='assignment',
            max_score=100,
            weight=50,
            date=timezone.now().date()
        )

        Grade.objects.create(
            student=self.student,
            assessment=self.assessment,
            score=85
        )
        Grade.objects.create(
            student=self.student,
            assessment=assessment2,
            score=90
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/grades/records/performance/?course_id={self.course.id}')

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.data['total_weighted_score'], 87.5)
