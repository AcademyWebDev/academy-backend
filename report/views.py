from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import StudentPerformanceReport, CoursePerformanceReport
from .serializers import StudentPerformanceReportSerializer, CoursePerformanceReportSerializer
from courses.models import Course


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentPerformanceReport.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()

    @action(detail=False, methods=['GET'])
    def student_performance(self, request):
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response({'error': 'Course ID is required'}, status=400)

        course = get_object_or_404(Course, id=course_id)

        if request.user.is_staff:
            reports = StudentPerformanceReport.objects.filter(course=course)
        else:
            reports, _ = StudentPerformanceReport.objects.get_or_create(
                student=request.user,
                course=course
            )
            reports = [reports]

        serializer = StudentPerformanceReportSerializer(reports, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def course_performance(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)

        reports = CoursePerformanceReport.objects.all()
        serializer = CoursePerformanceReportSerializer(reports, many=True)
        return Response(serializer.data)
