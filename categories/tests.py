from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

from accounts.models import User


class CategoryListViewTestCase(APITestCase):
    def setUp(self):
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

    def test_authorized_category_list(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        response = self.client.get(reverse('category_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_category_list(self):
        self.client = APIClient()

        response = self.client.get(reverse('category_list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
