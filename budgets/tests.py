from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

from accounts.models import User
from categories.models import Category


class BudgetCreateViewTestCase(APITestCase):
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

        Category.objects.create(name='house')

    def test_authorized_budget_create(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_budget_create(self):
        self.client = APIClient()

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_category(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_amount(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_start_at(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_end_at(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': '2023-11-10'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unvalid_category(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'UNVALID',
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unvalid_amount(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 'string',
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_unvalid_start_at(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': 'UNVALID',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_unvalid_end_at(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': 99999
            }
        ]

        response = self.client.post(
            path=reverse('budget-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
