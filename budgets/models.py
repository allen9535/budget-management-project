from django.db import models

from accounts.models import User
from categories.models import Category


class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='사용자'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='카테고리'
    )

    amount = models.PositiveIntegerField(verbose_name='금액')
    start_at = models.DateField(verbose_name='기간 시작일')
    end_at = models.DateField(verbose_name='기간 종료일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
