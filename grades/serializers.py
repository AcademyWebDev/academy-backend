from rest_framework import serializers
from .models import Assessment, Grade

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'assessment', 'score', 'submitted_at']
        read_only_fields = ['submitted_at']