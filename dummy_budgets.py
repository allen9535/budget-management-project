import django
import os
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from categories.models import Category
from budgets.models import Budget

if __name__ == '__main__':
    categories = Category.objects.all()

    for category in categories:
        for i in range(1, 11):
            Budget.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 10000),
                start_at=datetime(2023, 9, 1),
                end_at=datetime(2023, 9, 30)
            )

            Budget.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 10000),
                start_at=datetime(2023, 10, 1),
                end_at=datetime(2023, 10, 31)
            )

            Budget.objects.create(
                user=User.objects.get(id=i),
                category=Category.objects.get(id=category.id),
                amount=(random.randint(1, 10) * 10000),
                start_at=datetime(2023, 11, 1),
                end_at=datetime(2023, 11, 30)
            )
