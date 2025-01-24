from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet

router = DefaultRouter()
router.register(r'', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]