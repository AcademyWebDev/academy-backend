from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.managers import CustomUserManager


class User(AbstractUser):
    STUDENT = 'student'
    LECTURER = 'lecturer'
    ADMINISTRATOR = 'admin'

    USER_TYPES = [
        (STUDENT, 'Student'),
        (LECTURER, 'Lecturer'),
        (ADMINISTRATOR, 'Administrator'),
    ]

    username = None
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.'
        }
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default=STUDENT,
        help_text='Designates the type of user and their permissions in the system'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text='Contact phone number for the user'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='User\'s date of birth'
    )
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    email_verification_token = models.CharField(max_length=100, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='User_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='User_permissions_set',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
