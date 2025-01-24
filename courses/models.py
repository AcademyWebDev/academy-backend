from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)


class Course(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_taught')

    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()
    max_students = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])

    credits = models.DecimalField(max_digits=4, decimal_places=1)
    is_active = models.BooleanField(default=True)

    def current_enrollment_count(self):
        return self.enrollment_set.count()

    def is_enrollment_available(self):
        return self.current_enrollment_count() < self.max_students

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    ENROLLMENT_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('dropped', 'Dropped')
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='pending')

    class Meta:
        unique_together = ('student', 'course')


class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
