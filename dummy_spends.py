from faker import Faker
import django
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from spends.models import Spend
from categories.models import Category
from accounts.models import User


fake = Faker('ko-kr')

if __name__ == '__main__':
    for i in range(1000):
        start_at_dummy = fake.date_between(start_date=datetime(2023, 1, 1))
        Spend.objects.create(
            user=User.objects.get(id=random.randint(1, 100)),
            category=Category.objects.get(id=random.randint(1, 10)),
            amount=(random.randint(1, 10) * 10000),
            memo=f'{i}번째 메모',
            spend_at=start_at_dummy
        )
