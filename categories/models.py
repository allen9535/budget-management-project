from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=10,
        verbose_name='카테고리명'
    )
