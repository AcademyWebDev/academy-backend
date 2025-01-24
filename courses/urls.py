from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/enroll/', CourseViewSet.as_view({'post': 'enroll'}), name='course-enroll'),
    path('<int:pk>/drop/', CourseViewSet.as_view({'post': 'drop'}), name='course-drop'),
]
