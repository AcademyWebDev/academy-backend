from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Enrollment
from .serializers import (
    CourseSerializer,
    CourseCreateUpdateSerializer,
    EnrollmentSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['POST'])
    def enroll(self, request, pk=None):
        course = self.get_object()

        # Check if course is active and enrollment is available
        if not course.is_active or not course.is_enrollment_available():
            return Response({
                'error': 'Course is not available for enrollment'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check prerequisites
        user_completed_courses = Enrollment.objects.filter(
            student=request.user,
            status='confirmed'
        ).values_list('course__id', flat=True)

        missing_prereqs = course.prerequisites.exclude(id__in=user_completed_courses)
        if missing_prereqs.exists():
            return Response({
                'error': 'You have not completed all prerequisites',
                'missing_prerequisites': CourseSerializer(missing_prereqs, many=True).data
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'status': 'confirmed'}
        )

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['POST'])
    def drop(self, request, pk=None):
        course = self.get_object()
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            enrollment.status = 'dropped'
            enrollment.save()
            return Response(status=status.HTTP_200_OK)
        except Enrollment.DoesNotExist:
            return Response({
                'error': 'You are not enrolled in this course'
            }, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=user)
