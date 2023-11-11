from faker import Faker
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User


fake = Faker('ko-kr')

if __name__ == '__main__':
    for i in range(100):
        User.objects.create_user(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            phone='010-1111-2222',
            password='qwerty123!@#',
            is_active=True
        )
