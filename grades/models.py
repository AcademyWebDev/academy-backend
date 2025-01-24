from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course
from accounts.models import User


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('final', 'Final Exam'),
        ('assignment', 'Assignment'),
        ('project', 'Project')
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)

    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    date = models.DateField()


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'assessment']
