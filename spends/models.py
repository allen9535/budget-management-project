from django.db import models
from django.urls import reverse

from accounts.models import User
from categories.models import Category


class Spend(models.Model):
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
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    spend_at = models.DateField(verbose_name='지출일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
