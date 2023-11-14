from faker import Faker
import django
import os
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from categories.models import Category
from spends.models import Spend

fake = Faker('ko-kr')

if __name__ == '__main__':
    categories = Category.objects.all()
    for category in categories:
        for i in range(1, 11):
            spend_at_dummy = fake.date_between(start_date=datetime(
                2023, 9, 1), end_date=datetime(2023, 9, 30))

            Spend.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 1000),
                memo=f'{i}번째 메모',
                spend_at=spend_at_dummy
            )

            spend_at_dummy = fake.date_between(start_date=datetime(
                2023, 10, 1), end_date=datetime(2023, 10, 31))

            Spend.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 1000),
                memo=f'{i}번째 메모',
                spend_at=spend_at_dummy
            )

            spend_at_dummy = fake.date_between(start_date=datetime(
                2023, 11, 1), end_date=datetime(2023, 11, 30))

            Spend.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 1000),
                memo=f'{i}번째 메모',
                spend_at=spend_at_dummy
            )

            Spend.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 1000),
                memo=f'{i}번째 메모',
                spend_at=datetime.now().date()
            )
