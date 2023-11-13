from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse


class SpendAuthorizedTestCase(APITestCase):
    fixtures = ['db_dump_data.json']

    def setUp(self):
        self.client = APIClient()

        self.login_data = {
            'username': 'yeongsugim',
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
            'category': 'house',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_no_category(self):
        request_data = {
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_amount(self):
        request_data = {
            'category': 'house',
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_memo(self):
        request_data = {
            'category': 'house',
            'amount': 10000,
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 201:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_no_spend_at(self):
        request_data = {
            'category': 'house',
            'amount': 10000,
            'memo': 'memo',
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_category(self):
        request_data = {
            'category': 'INVALID',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_amount(self):
        request_data = {
            'category': 'test',
            'amount': 'INVALID',
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_spend_at(self):
        request_data = {
            'category': 'test',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': 20231110
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_default(self):
        params = {
            'start_at': '2023-02-01',
            'end_at': '2023-10-31',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_no_params(self):
        response = self.client.get(reverse('spend_list'))

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_no_category(self):
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

    def test_list_no_min_amount(self):
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

    def test_list_no_max_amount(self):
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

    def test_list_no_start_at(self):
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

    def test_list_no_end_at(self):
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

    def test_list_invalid_start_at(self):
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

    def test_list_invalid_end_at(self):
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

    def test_list_invalid_category(self):
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

    def test_list_invalid_min_amount(self):
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

    def test_list_invalid_max_amount(self):
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

    def test_list_under_zero_min_amount(self):
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

    def test_detail_default(self):
        response = self.client.get(
            '/api/v1/spends/detail/12'
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
            '/api/v1/spends/detail/1'
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/spends/detail/12/update/',
            update_data
        )

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_wrong_spend_no(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/spends/detail/1/update/',
            update_data
        )

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_update_wrong_value(self):
        update_data = {
            'amount': 'INVALID'
        }

        response = self.client.put(
            '/api/v1/spends/detail/12/update/',
            update_data
        )

        if response.status_code != 400:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_default(self):
        response = self.client.delete('/api/v1/spends/detail/12/delete/')

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_wrong_spend_no(self):
        response = self.client.delete('/api/v1/spends/detail/1/delete/')

        if response.status_code != 406:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_list_exclude_default(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000,
            'exclude': 12
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_exclude_invalid_exclude(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000,
            'exclude': 'INVALID'
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 200:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SpendUnauthorizedTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_default(self):
        request_data = {
            'category': 'house',
            'amount': 10000,
            'memo': 'memo',
            'spend_at': '2023-11-10'
        }

        response = self.client.post(reverse('spend_create'), request_data)

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_default(self):
        params = {
            'start_at': '2023-11-02',
            'end_at': '2023-11-04',
            'category': 'house',
            'min_amount': 10000,
            'max_amount': 20000
        }

        response = self.client.get(reverse('spend_list'), params)

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_default(self):
        response = self.client.get(
            '/api/v1/spends/detail/12'
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_default(self):
        update_data = {
            'amount': 5000
        }

        response = self.client.put(
            '/api/v1/spends/detail/12/update/',
            update_data
        )

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_default(self):
        response = self.client.delete('/api/v1/spends/detail/12/delete/')

        if response.status_code != 401:
            print(response.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
