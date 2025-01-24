from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Case, When, Value, IntegerField
from django.utils import timezone
from attendance.models import AttendanceSession, Attendance
from attendance.serializers import AttendanceSessionSerializer, AttendanceSerializer



class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def terminate(self, request, pk=None):
        session = self.get_object()
        session.terminate_session()
        return Response({'status': 'Session terminated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def check_in(self, request, pk=None):
        session = self.get_object()

        if not session.is_active:
            return Response({'error': 'Session is not active'}, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not session.is_valid_location(latitude, longitude):
            return Response({'error': 'Outside allowed location'}, status=status.HTTP_403_FORBIDDEN)

        attendance, created = Attendance.objects.get_or_create(
            student=request.user,
            session=session,
            defaults={
                'latitude': latitude,
                'longitude': longitude
            }
        )

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_200_OK)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Attendance.objects.all()
        return Attendance.objects.filter(student=user)

    @action(detail=False, methods=['GET'])
    def attendance_percentage(self, request):
        user = request.user
        course_id = request.query_params.get('course_id')

        attendances = Attendance.objects.filter(
            student=user,
            session__course_id=course_id
        )

        total_sessions = AttendanceSession.objects.filter(course_id=course_id).count()
        attended_sessions = attendances.count()

        percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0

        return Response({
            'total_sessions': total_sessions,
            'attended_sessions': attended_sessions,
            'attendance_percentage': round(percentage, 2)
        })
