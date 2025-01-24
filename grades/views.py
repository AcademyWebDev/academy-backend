from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Assessment, Grade
from .serializers import AssessmentSerializer, GradeSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Grade.objects.all()
        return Grade.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only teachers can record grades'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def performance(self, request):
        course_id = request.query_params.get('course_id')

        grades = Grade.objects.filter(
            student=request.user,
            assessment__course_id=course_id
        )

        total_weighted_score = sum(
            grade.score * (grade.assessment.weight / 100)
            for grade in grades
        )

        return Response({
            'total_weighted_score': total_weighted_score
        })