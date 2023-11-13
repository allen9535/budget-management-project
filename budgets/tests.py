from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse


class BudgetViewAuthorizedTestCase(APITestCase):
    fixtures = ['db_dump_data.json']

    def setUp(self):
        self.client = APIClient()

        self.login_data = {
            'username': 'wo',
            'password': 'qwerty123!@#'
        }

        self.access_token = self.client.post(
            reverse('login'),
            self.login_data
        ).data.get('access')

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

    def test_create_default(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                'house': 1000000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_multiple_data(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                'house': 1000000,
                'food': 100000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_no_category(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                '': 1000000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_no_amount(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                'house': ''
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_no_start_at(self):
        request_data = {
            'end_at': '2023-11-11',
            'budgets': {
                'house': 1000000,
                'food': 100000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_end_at(self):
        request_data = {
            'start_at': '2023-11-10',
            'budgets': {
                'house': 1000000,
                'food': 100000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_category(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                'INVALID': 1000000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_amount(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': '2023-11-11',
            'budgets': {
                'house': 'INVALID'
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_start_at(self):
        request_data = {
            'start_at': 'INVALID',
            'end_at': '2023-11-11',
            'budgets': {
                'house': 1000000,
                'food': 100000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_end_at(self):
        request_data = {
            'start_at': '2023-11-10',
            'end_at': 'INVALID',
            'budgets': {
                'house': 1000000,
                'food': 100000
            }
        }

        response = self.client.post(
            path=reverse('budget_create'),
            data=request_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_default(self):
        response = self.client.get(reverse('budget_list'))

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_default(self):
        response = self.client.get(
            '/api/v1/budgets/detail/80'
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_invalid_budget_no(self):
        response = self.client.get(
            '/api/v1/budgets/detail/INVALID'
        )

        if response.status_code != 404:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_wrong_budget_no(self):
        response = self.client.get(
            '/api/v1/budgets/detail/2'
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/80/update/',
            update_data
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_budget_no(self):
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

    def test_update_wrong_budget_no(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/budgets/detail/1/update/',
            update_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_update_invalid_value(self):
        update_data = {
            'amount': 'INVALID'
        }

        response = self.client.put(
            '/api/v1/budgets/detail/1/update/',
            update_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_delete_default(self):
        response = self.client.delete(
            '/api/v1/budgets/detail/80/delete/'
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_invalid_budget_no(self):
        response = self.client.delete(
            '/api/v1/budgets/detail/INVALID/delete/'
        )

        if response.status_code != 404:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wrong_budget_no(self):
        response = self.client.delete(
            '/api/v1/budgets/detail/1/delete/'
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_recommend_default(self):
        request_data = {
            'amount': 100000
        }

        response = self.client.post(reverse('budget_recommend'), request_data)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recommend_invalid_data(self):
        request_data = {
            'amount': 'INVALID'
        }

        response = self.client.post(
            reverse('budget_recommend'), request_data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_406_NOT_ACCEPTABLE
        )

    def test_recommend_wrong_data(self):
        request_data = {
            'amount': 0
        }

        response = self.client.post(reverse('budget_recommend'), request_data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_406_NOT_ACCEPTABLE
        )


class BudgetViewUnauthorizedTestCase(APITestCase):
    def test_create_unauthorized(self):
        response_data = [
            {
                'category': 'house',
                'amount': 10000,
                'start_at': '2023-11-10',
                'end_at': '2023-11-11'
            }
        ]

        response = self.client.post(
            path=reverse('budget_create'),
            data=response_data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_unauthorized(self):
        response = self.client.get(reverse('budget_list'))

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_unauthorized(self):
        response = self.client.get(
            '/api/v1/budgets/detail/1'
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_unauthorized(self):
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

    def test_delete_unauthorized(self):
        response = self.client.delete(
            '/api/v1/budgets/detail/1/delete/'
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recommend_unauthorized(self):
        budget_data = {
            'amount': 100000
        }

        response = self.client.post(reverse('budget_recommend'), budget_data)

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
