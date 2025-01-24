# courses/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Course, CourseCategory, Enrollment

User = get_user_model()


class CourseModelTests(TestCase):
    def setUp(self):
        self.category = CourseCategory.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Course Description',
            category=self.category,
            instructor=self.instructor,
            difficulty_level='beginner',
            start_date='2024-01-01',
            end_date='2024-04-30',
            max_students=30,
            credits=3.0
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.code, 'TEST101')
        self.assertTrue(self.course.is_active)

    def test_enrollment_availability(self):
        self.assertTrue(self.course.is_enrollment_available())


class CourseEnrollmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        self.category = CourseCategory.objects.create(
            name='Test Category'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            category=self.category,
            instructor=self.instructor,
            start_date='2024-01-01',
            end_date='2024-04-30',
            max_students=30,
            difficulty_level='beginner',
            credits=3.0
        )

    def test_student_enrollment(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(
            student=self.student,
            course=self.course
        ).exists())

    def test_course_prerequisites(self):
        prerequisite_course = Course.objects.create(
            title='Prerequisite Course',
            code='PREREQ101',
            category=self.category,
            instructor=self.instructor,
            start_date='2024-01-01',
            end_date='2024-04-30',
            max_students=30,
            difficulty_level='beginner',
            credits=3.0
        )
        self.course.prerequisites.add(prerequisite_course)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseDropTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            start_date='2024-01-01',
            end_date='2024-04-30',
            max_students=30,
            difficulty_level='beginner',
            credits=3.0
        )
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='confirmed'
        )

    def test_course_drop(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.id}/drop/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enrollment = Enrollment.objects.get(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.status, 'dropped')


class CourseCapacityTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Full Capacity Course',
            code='FULL101',
            start_date='2024-01-01',
            end_date='2024-04-30',
            max_students=2,
            difficulty_level='beginner',
            credits=3.0
        )
        self.students = [
            User.objects.create_user(
                email=f'student{i}@example.com',
                password='testpass123'
            ) for i in range(3)
        ]

    def test_course_capacity_limit(self):
        client = APIClient()

        for student in self.students[:2]:
            client.force_authenticate(user=student)
            response = client.post(f'/api/courses/{self.course.id}/enroll/')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        client.force_authenticate(user=self.students[2])
        response = client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)