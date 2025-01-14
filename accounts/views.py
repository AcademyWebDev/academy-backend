import uuid
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer, ChangePasswordSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            return Response({
                'message': 'Registration successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    SUCCESS_STATUS = status.HTTP_200_OK
    FAILURE_STATUS = status.HTTP_400_BAD_REQUEST
    REFRESH_TOKEN_KEY = "refresh_token"

    def post(self, request):
        try:
            refresh_token = self._get_refresh_token(request)
            self._blacklist_refresh_token(refresh_token)
            return Response(status=self.SUCCESS_STATUS)
        except KeyError:
            return Response({"error": "Refresh token missing"}, status=self.FAILURE_STATUS)
        except Exception as e:
            return Response({"error": str(e)}, status=self.FAILURE_STATUS)

    def _get_refresh_token(self, request):
        return request.data[self.REFRESH_TOKEN_KEY]

    def _blacklist_refresh_token(self, refresh_token):
        token = RefreshToken(refresh_token)
        token.blacklist()



class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    SUCCESS_STATUS = status.HTTP_204_NO_CONTENT

    def change_password(self, current_user, validated_data):
        current_user.set_password(validated_data['new_password'])
        current_user.save()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.change_password(request.user, serializer.validated_data)
        return Response(status=self.SUCCESS_STATUS)

    def put(self, request):
        return self.post(request)



class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



class TokenVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self, request):
        token = request.data.get('token')
        try:
            RefreshToken(token).verify()
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            reset_token = str(uuid.uuid4())
            user.password_reset_token = reset_token
            user.save()

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            send_mail(
                'Password Reset Request',
                f'Click here to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({
                'message': 'Password reset email sent'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'No user found with this email'
            }, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(new_password)
            user.password_reset_token = None
            user.save()

            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class DeactivateAccountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()

        return Response({
            'message': 'Account deactivated successfully'
        }, status=status.HTTP_200_OK)


class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.delete()
