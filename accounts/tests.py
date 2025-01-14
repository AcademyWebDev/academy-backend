from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        self.test_user = User.objects.create_user(
            email='existing@example.com',
            password='ExistingPass123!',
            first_name='Existing',
            last_name='User'
        )
        self.refresh = RefreshToken.for_user(self.test_user)
        self.access_token = str(self.refresh.access_token)

    def get_auth_header(self):
        return {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_user_registration_success(self):
        url = reverse('accounts:register')
        response = self.client.post(url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(User.objects.count(), 2)

    def test_user_registration_duplicate_email(self):
        url = reverse('accounts:register')
        self.client.post(url, self.user_data, format='json')
        response = self.client.post(url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login_success(self):
        url = reverse('accounts:login')
        self.client.post(reverse('accounts:register'), self.user_data, format='json')
        response = self.client.post(url, self.login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_wrong_credentials(self):
        url = reverse('accounts:login')
        wrong_data = {
            'email': 'test@example.com',
            'password': 'WrongPass123!'
        }
        response = self.client.post(url, wrong_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_user_logout_success(self):
    #     url = reverse('accounts:logout')
    #     response = self.client.post(url, **self.get_auth_header())
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_unauthorized(self):
        url = reverse('accounts:logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_success(self):
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'ExistingPass123!',
            'new_password': 'NewPass123!'
        }
        response = self.client.post(url, data, **self.get_auth_header())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        login_response = self.client.post(reverse('accounts:login'), {
            'email': 'existing@example.com',
            'password': 'NewPass123!'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_password_change_wrong_old_password(self):
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'WrongPass123!',
            'new_password': 'NewPass123!'
        }
        response = self.client.post(url, data, **self.get_auth_header())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile_success(self):
        url = reverse('accounts:profile')
        response = self.client.get(url, **self.get_auth_header())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@example.com')

    def test_update_profile_success(self):
        url = reverse('accounts:profile')
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, update_data, **self.get_auth_header())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')

    def test_get_profile_unauthorized(self):
        url = reverse('accounts:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        url = reverse('accounts:token-refresh')
        data = {'refresh': str(self.refresh)}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        url = reverse('accounts:token-refresh')
        data = {'refresh': 'invalid-token'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_forgot_password_success(self):
    #     url = reverse('accounts:forgot-password')
    #     data = {'email': 'existing@example.com'}
    #     response = self.client.post(url, data)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('message', response.data)

    def test_forgot_password_invalid_email(self):
        url = reverse('accounts:forgot-password')
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

