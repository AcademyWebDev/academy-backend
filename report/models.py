from django.db import models
from django.db.models import Avg, Sum
from accounts.models import User
from courses.models import Course
from attendance.models import Attendance, AttendanceSession
from grades.models import Grade, Assessment


class StudentPerformanceReport(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    total_assessments = models.IntegerField(default=0)
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_report(cls, student, course):
        total_assessments = Assessment.objects.filter(course=course).count()

        avg_grade = Grade.objects.filter(
            assessment__course=course,
            student=student
        ).aggregate(Avg('score'))['score__avg'] or 0

        total_sessions = AttendanceSession.objects.filter(course=course).count()
        attended_sessions = Attendance.objects.filter(
            student=student,
            session__course=course
        ).count()

        attendance_percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0

        return cls.objects.create(
            student=student,
            course=course,
            total_assessments=total_assessments,
            average_grade=avg_grade,
            attendance_percentage=attendance_percentage
        )


class CoursePerformanceReport(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    total_students = models.IntegerField(default=0)
    average_course_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    overall_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_report(cls, course):
        students = User.objects.filter(enrollment__course=course)
        total_students = students.count()

        avg_course_grade = Grade.objects.filter(
            assessment__course=course
        ).aggregate(Avg('score'))['score__avg'] or 0

        total_sessions = AttendanceSession.objects.filter(course=course).count()
        total_attendances = Attendance.objects.filter(session__course=course).count()
        overall_attendance_rate = (
            (total_attendances / (total_students * total_sessions) * 100)
            if total_students > 0 and total_sessions > 0
            else 0
        )

        return cls.objects.create(
            course=course,
            total_students=total_students,
            average_course_grade=avg_course_grade,
            overall_attendance_rate=overall_attendance_rate
        )
