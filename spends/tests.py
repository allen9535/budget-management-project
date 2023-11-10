from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse

import pandas as pd

from accounts.models import User
from categories.models import Category
from .models import Spend


class SpendCreateAuthorizedTestCase(APITestCase):
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

        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        Category.objects.create(name='test')

    def test_default(self):
        data = {
            'category': 'test',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_category(self):
        data = {
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_amount(self):
        data = {
            'category': 'test',
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_memo(self):
        data = {
            'category': 'test',
            'amount': 10000,
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_spend_at(self):
        data = {
            'category': 'test',
            'amount': 10000,
            'memo': 'memo',
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category(self):
        data = {
            'category': 'INVALID',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_amount(self):
        data = {
            'category': 'test',
            'amount': 'INVALID',
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_spend_at(self):
        data = {
            'category': 'test',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': 20231110
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)


class SpendCreateUnauthorizedTestCase(APITestCase):
    def setUp(self):
        Category.objects.create(name='test')

    def test_default(self):
        self.client = APIClient()

        data = {
            'category': 'test',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), data)

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SpendListAuthorizedTestCase(APITestCase):
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

        self.client = APIClient()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        dummy_category = pd.read_csv('category_list.csv').category
        for category in dummy_category:
            Category.objects.create(name=category)

        for i in range(0, 7, 2):
            Spend.objects.create(
                user=User.objects.get(id=1),
                category=Category.objects.get(name=dummy_category[i]),
                amount=((i + 1) * 10000),
                memo=f'{i}',
                spend_at=f'2023-11-{(i + 1) * 2}'
            )

            Spend.objects.create(
                user=User.objects.get(id=1),
                category=Category.objects.get(name=dummy_category[i]),
                amount=((i + 2) * 10000),
                memo=f'{i + 1}',
                spend_at=f'2023-11-{(i + 2) * 2}'
            )

    def test_default(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_params(self):
        response = self.client.get(reverse('spend_list'))

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_category(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_min_amount(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_max_amount(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_start_at(self):
        params = {
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_end_at(self):
        params = {
            'start_at': '2023-11-02',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_start_at(self):
        params = {
            'start_at': 'INVALID',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_end_at(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': 'INVALID',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_category(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'INVALID',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_min_amount(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 'INVALID',
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_max_amount(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 'INVALID'
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_under_zero_min_amount(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': -10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SpendListUnauthorizedTestCase(APITestCase):
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

        self.client = APIClient()

        dummy_category = pd.read_csv('category_list.csv').category
        for category in dummy_category:
            Category.objects.create(name=category)

        for i in range(0, 7, 2):
            Spend.objects.create(
                user=User.objects.get(id=1),
                category=Category.objects.get(name=dummy_category[i]),
                amount=((i + 1) * 10000),
                memo=f'{i}',
                spend_at=f'2023-11-{(i + 1) * 2}'
            )

            Spend.objects.create(
                user=User.objects.get(id=1),
                category=Category.objects.get(name=dummy_category[i]),
                amount=((i + 2) * 10000),
                memo=f'{i + 1}',
                spend_at=f'2023-11-{(i + 2) * 2}'
            )

    def test_default(self):
        data = {
            'category': 'house',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_list'), data)

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SpendDetailAuthorizedTestCase(APITestCase):
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

        Category.objects.create(name='test')

        Spend.objects.create(
            user=User.objects.get(id=1),
            category=Category.objects.get(name='test'),
            amount=10000,
            memo='memo',
            spend_at='2023-11-10'
        )

        Spend.objects.create(
            user=User.objects.get(id=2),
            category=Category.objects.get(name='test'),
            amount=20000,
            memo='memo',
            spend_at='2023-11-11'
        )

    def test_detail_default(self):
        response = self.client.get(
            '/api/v1/spends/detail/1'
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_invalid_spend_no(self):
        response = self.client.get(
            '/api/v1/spends/detail/invalid'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_wrong_spend_no(self):
        response = self.client.get(
            '/api/v1/spends/detail/2'
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_detail_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/spends/detail/1/update/',
            update_data
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_update_wrong_spend_no(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/spends/detail/2/update/',
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
            '/api/v1/spends/detail/1/update/',
            update_data
        )

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detail_delete_default(self):
        response = self.client.delete('/api/v1/spends/detail/1/delete/')

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_delete_wrong_spend_no(self):
        response = self.client.delete('/api/v1/spends/detail/2/delete/')

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
