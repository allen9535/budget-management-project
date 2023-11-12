from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

from accounts.models import User
from categories.models import Category
from .models import Budget


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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
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
            path=reverse('budget_create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)


class BudgetListTestCase(APITestCase):
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

        Category.objects.create(name='category1')
        Category.objects.create(name='category2')

        Budget.objects.create(
            user=User.objects.get(id=1),
            category=Category.objects.get(id=1),
            amount=10000,
            start_at='2023-11-12',
            end_at='2023-11-13'
        )
        Budget.objects.create(
            user=User.objects.get(id=1),
            category=Category.objects.get(id=2),
            amount=20000,
            start_at='2023-11-11',
            end_at='2023-11-12'
        )

    def test_authorized(self):
        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        response = self.client.get(reverse('budget_list'))

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized(self):
        response = self.client.get(reverse('budget_list'))

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BudgetDetailAuthorizedTestCase(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            email='test@email.com',
            password='qwerty123!@#',
            is_active=True
        )
        User.objects.create_user(
            username='test2',
            email='test2@email.com',
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

        Category.objects.create(name='category1')
        Category.objects.create(name='category2')

        Budget.objects.create(
            user=User.objects.get(id=1),
            category=Category.objects.get(id=1),
            amount=10000,
            start_at='2023-11-12',
            end_at='2023-11-13'
        )
        Budget.objects.create(
            user=User.objects.get(id=2),
            category=Category.objects.get(id=2),
            amount=20000,
            start_at='2023-11-11',
            end_at='2023-11-12'
        )

    def test_default(self):
        response = self.client.get(
            '/api/v1/budgets/detail/1'
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_budget_no(self):
        response = self.client.get(
            '/api/v1/budgets/detail/INVALID'
        )

        if response.status_code != 404:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_budget_no(self):
        response = self.client.get(
            '/api/v1/budgets/detail/2'
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_detail_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/1/update/',
            update_data
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_update_invalid_budget_no(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/INVALID/update/',
            update_data
        )

        if response.status_code != 404:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_update_wrong_budget_no(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/2/update/',
            update_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_detail_update_wrong_value(self):
        update_data = {
            'amount': 'INVALID'
        }

        response = self.client.put(
            '/api/v1/budgets/detail/1/update/',
            update_data
        )

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BudgetDetailUnauthorizedTestCase(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            email='test@email.com',
            password='qwerty123!@#',
            is_active=True
        )
        User.objects.create_user(
            username='test2',
            email='test2@email.com',
            password='qwerty123!@#',
            is_active=True
        )

        Category.objects.create(name='category1')
        Category.objects.create(name='category2')

        Budget.objects.create(
            user=User.objects.get(id=1),
            category=Category.objects.get(id=1),
            amount=10000,
            start_at='2023-11-12',
            end_at='2023-11-13'
        )
        Budget.objects.create(
            user=User.objects.get(id=2),
            category=Category.objects.get(id=2),
            amount=20000,
            start_at='2023-11-11',
            end_at='2023-11-12'
        )

    def test_default(self):
        response = self.client.get(
            '/api/v1/budgets/detail/1'
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/1/update/',
            update_data
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
