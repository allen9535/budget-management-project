from celery import shared_task

from django.db.models.functions import Coalesce
from django.db.models import Sum

from django.core.mail import send_mail

from accounts.models import User
from budgets.models import Budget
from categories.models import Category
from .models import Spend

from dotenv import load_dotenv

from datetime import datetime, timedelta

import os

load_dotenv()


ALL_USERS = User.objects.all()
CATEGORIES = Category.objects.all()


@shared_task
def total_spend_consulting(user_budgets, user_spends, period_start, period_end):
    period_budgets = user_budgets.filter(
        start_at__gte=period_start,
        end_at__lte=period_end
    )
    period_spends = user_spends.filter(
        spend_at__gte=period_start,
        spend_at__lte=period_end
    )

    period_budgets_sum = period_budgets.aggregate(
        sum=Coalesce(Sum('amount'), 0)
    ).get('sum')
    period_spends_sum = period_spends.aggregate(
        sum=Coalesce(Sum('amount'), 0)
    ).get('sum')

    rest_budget = period_budgets_sum - period_spends_sum
    rest_days = (
        period_end - datetime.now().date() + timedelta(days=1)
    ).days

    can_spend_per_last_days = int(round((rest_budget / rest_days), -2))

    return can_spend_per_last_days


@shared_task
def category_spend_consulting(user_budgets, user_spends, period_start, period_end):
    messages = {}

    for category in CATEGORIES:
        category_budgets = user_budgets.filter(
            category=category.id,
            start_at__gte=period_start,
            end_at__lte=period_end
        )

        category_spends = user_spends.filter(
            category=category.id,
            spend_at__gte=period_start,
            spend_at__lte=period_end
        )

        period_budgets_sum = category_budgets.aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')
        period_spends_sum = category_spends.aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        rest_budget = period_budgets_sum - period_spends_sum
        rest_days = (
            period_end - datetime.now().date() + timedelta(days=1)
        ).days

        can_spend_per_last_days = int(round((rest_budget / rest_days), -2))

        messages[category.name] = can_spend_per_last_days

    return messages


@shared_task
def send_messages_to_customer():
    email_subject = '[예산 관리 서비스] 오늘 예산에 대한 컨설팅입니다!'

    for i in range(1, 2):
        user = ALL_USERS.get(id=i)

        user_budgets = Budget.objects.filter(user=user)
        user_spends = Spend.objects.filter(user=user)

        last_budget = user_budgets.last()

        total_spend_consulting_data = total_spend_consulting(
            user_budgets,
            user_spends,
            last_budget.start_at,
            last_budget.end_at
        )
        category_spend_consulting_data = category_spend_consulting(
            user_budgets,
            user_spends,
            last_budget.start_at,
            last_budget.end_at
        )

        email_body = ''
        if total_spend_consulting_data <= 0:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {total_spend_consulting_data:,}원 입니다! 전체 예산을 이미 초과하셨어요! 더 나은 소비 습관을 위해 노력합시다!\n \n \n'
        elif total_spend_consulting_data < 10000:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {total_spend_consulting_data:,}원 입니다! 곧 예산을 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n \n'
        else:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 총 {total_spend_consulting_data:,}원\n아직 여유가 있네요! 남은 일자도 힘내세요!\n \n \n'

        for key, value in category_spend_consulting_data.items():
            if value <= 0:
                email_body += f'금일 {key} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {value:,}원 입니다! 해당 항목에서 사용 가능한 예산을 이미 초과하셨어요! 이렇게 되면 전체 예산이 흔들리게 됩니다! 더 나은 소비 습관을 위해 노력해주세요!\n \n'
            elif value < 5000:
                email_body += f'금일 {key} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {value:,}원 입니다! 해당 카테고리에서 사용 가능한 예산을 곧 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n'
            else:
                email_body += f'금일 {key} 항목에서 사용 가능한 금액은 총 {value:,}원\n예산을 잘 관리하고 계시네요! 남은 기간도 파이팅!\n \n'

            email_body += f'\n'

        send_mail(
            email_subject,
            email_body,
            os.getenv('EMAIL_HOST_USER'),
            ['allen9535@naver.com']
        )
