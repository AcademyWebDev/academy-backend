from django.db import models
from courses.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade_value = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_by = models.ForeignKey(User, related_name='submitted_grades', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
