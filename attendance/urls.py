# attendance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceSessionViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register(r'records', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    # Custom routes for specific actions
    path('sessions/<int:pk>/terminate/',
         AttendanceSessionViewSet.as_view({'post': 'terminate'}),
         name='attendance-session-terminate'),
    path('sessions/<int:pk>/check_in/',
         AttendanceSessionViewSet.as_view({'post': 'check_in'}),
         name='attendance-session-check-in'),
    path('records/percentage/',
         AttendanceViewSet.as_view({'get': 'attendance_percentage'}),
         name='attendance-percentage')
]