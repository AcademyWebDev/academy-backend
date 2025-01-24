from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, GradeViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet)
router.register(r'records', GradeViewSet, basename='grade')

urlpatterns = [
    path('', include(router.urls)),
    path('records/performance/',
         GradeViewSet.as_view({'get': 'course_performance'}),
         name='course-performance'),
    path('records/statistics/',
         GradeViewSet.as_view({'get': 'course_grade_statistics'}),
         name='course-grade-statistics'),
    path('records/gpa/',
         GradeViewSet.as_view({'get': 'student_overall_gpa'}),
         name='student-gpa')
]