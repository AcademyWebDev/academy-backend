from rest_framework import serializers
from .models import Course, CourseCategory, Enrollment

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    current_enrollment = serializers.SerializerMethodField()
    prerequisites_details = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'code', 'description', 'category',
            'instructor', 'instructor_name', 'difficulty_level',
            'prerequisites', 'prerequisites_details',
            'start_date', 'end_date', 'max_students',
            'current_enrollment', 'credits', 'is_active'
        ]
        read_only_fields = ['current_enrollment']

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None

    def get_current_enrollment(self, obj):
        return obj.current_enrollment_count()

    def get_prerequisites_details(self, obj):
        return CourseSerializer(obj.prerequisites.all(), many=True).data

class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['id']

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_details', 'enrolled_at', 'status']
        read_only_fields = ['enrolled_at']
