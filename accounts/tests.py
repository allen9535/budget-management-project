from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

from .models import User


class UserSignupViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.user_data = {
            'username': 'test',
            'email': 'test@email.com',
            'phone': '010-1111-2222',
            'password': 'qwerty123!@#',
            'check_password': 'qwerty123!@#'
        }

    def test_correct_signup(self):
        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_username(self):
        self.user_data['username'] = ''

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password(self):
        self.user_data['password'] = ''

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_check_password(self):
        self.user_data['check_password'] = ''

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self):
        self.user_data['email'] = ''

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_phone(self):
        self.user_data['phone'] = ''

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_email(self):
        self.user_data['email'] = 'abcdefg'

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_password(self):
        self.user_data['password'] = '1234'

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_phone(self):
        self.user_data['phone'] = '12341234'

        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='test',
            email='test@email.com',
            password='qwerty123!@#',
            is_active=True
        )
        self.data = {
            'username': 'test',
            'password': 'qwerty123!@#'
        }

    def test_login(self):
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_not_verified(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_username(self):
        self.data['username'] = 'ttest'

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_password(self):
        self.data['password'] = 'testtest'

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserLogoutViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('logout')

        User.objects.create_user(
            username='test',
            email='test@email.com',
            password='qwerty123!@#',
            is_active=True
        )

        self.login_data = {
            'username': 'test',
            'password': 'qwerty123!@#'
        }

        self.access_token = self.client.post(
            reverse('login'),
            self.login_data
        ).data.get('access')

        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

    def test_logout(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
