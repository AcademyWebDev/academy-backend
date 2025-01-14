from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('register/',
         UserRegistrationView.as_view(),
         name='register'),

    path('login/',
         UserLoginView.as_view(),
         name='login'),

    path('logout/',
         LogoutView.as_view(),
         name='logout'),

    path('change-password/',
         ChangePasswordView.as_view(),
         name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),

    path('reset-password/<str:token>/',
         ResetPasswordView.as_view(),
         name='reset-password'),

    path('login/refresh/',
         TokenRefreshView.as_view(),
         name='token-refresh'),

    path('profile/',
         UserProfileView.as_view(),
         name='profile'),
]
