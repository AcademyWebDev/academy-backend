from rest_framework import serializers
from .models import StudentPerformanceReport, CoursePerformanceReport

class StudentPerformanceReportSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentPerformanceReport
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.get_full_name()

    def get_course_name(self, obj):
        return obj.course.title

class CoursePerformanceReportSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = CoursePerformanceReport
        fields = '__all__'

    def get_course_name(self, obj):
        return obj.course.title
