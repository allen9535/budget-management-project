import django
import pandas as pd
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from categories.models import Category


if __name__ == '__main__':
    categories = pd.read_csv('category_list.csv').category
    for category in categories:
        Category.objects.create(name=category)