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
def send_messages_to_customer():
    email_subject = '[예산 관리 서비스] 오늘 예산에 대한 컨설팅입니다!'

    # for i in range(1, ALL_USERS.count()): # 실사용
    for i in range(1, 2):  # 테스트용
        user = ALL_USERS.get(id=i)

        user_budgets = Budget.objects.filter(user=user)
        user_spends = Spend.objects.filter(user=user)

        last_budget = user_budgets.last()

        total_budget_sum = user_budgets.filter(
            start_at__gte=last_budget.start_at,
            end_at__lte=last_budget.end_at
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')
        total_spend_sum = user_spends.filter(
            spend_at__gte=last_budget.start_at,
            spend_at__lte=last_budget.end_at
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        can_spend_per_last_days = int(
            round(
                (
                    (total_budget_sum - total_spend_sum) /
                    (last_budget.end_at - datetime.now().date() + timedelta(days=1)).days
                ), -2
            )
        )

        email_body = ''
        if can_spend_per_last_days <= 0:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 전체 예산을 이미 초과하셨어요! 더 나은 소비 습관을 위해 노력합시다!\n \n \n'
        elif can_spend_per_last_days < 10000:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 곧 예산을 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n \n'
        else:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 총 {can_spend_per_last_days:,}원\n아직 여유가 있네요! 남은 일자도 힘내세요!\n \n \n'

        for category in CATEGORIES:
            category_budget_sum = user_budgets.filter(
                category=category.id,
                start_at__gte=last_budget.start_at,
                end_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            category_spend_sum = user_spends.filter(
                category=category.id,
                spend_at__gte=last_budget.start_at,
                spend_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            can_spend_per_last_days = int(
                round(
                    (
                        (category_budget_sum - category_spend_sum) /
                        (last_budget.end_at - datetime.now().date() +
                         timedelta(days=1)).days
                    ), -2
                )
            )

            if can_spend_per_last_days <= 0:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 해당 항목에서 사용 가능한 예산을 이미 초과하셨어요! 이렇게 되면 전체 예산이 흔들리게 됩니다! 더 나은 소비 습관을 위해 노력해주세요!\n \n'
            elif can_spend_per_last_days < 5000:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 해당 카테고리에서 사용 가능한 예산을 곧 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n'
            else:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 {can_spend_per_last_days:,}원\n예산을 잘 관리하고 계시네요! 남은 기간도 파이팅!\n \n'

            email_body += f'\n'

        send_mail(
            email_subject,
            email_body,
            os.getenv('EMAIL_HOST_USER'),
            ['allen9535@naver.com']  # 테스트용
            # [user.email for user in ALL_USERS] # 실사용
        )


@shared_task
def send_result_to_customer():
    email_subject = '[예산 관리 서비스] 오늘 지출 내역에 대한 안내입니다!'
    today_date = datetime.now().date()

    # for i in range(ALL_USERS.count()): # 실사용
    for i in range(1, 2):  # 테스트용
        email_body = ''

        user = ALL_USERS.get(id=i)

        user_budgets = Budget.objects.filter(user=user)
        user_spends = Spend.objects.filter(user=user)

        last_budget = user_budgets.last()

        today_spend_sum = user_spends.filter(
            spend_at=today_date
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        email_body += f'오늘 지출한 총액: {today_spend_sum:,}원\n\n'

        for category in CATEGORIES:
            category_budget_sum = user_budgets.filter(
                category=category,
                start_at__gte=last_budget.start_at,
                end_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            category_spend_sum = user_spends.filter(
                category=category,
                spend_at=today_date
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            email_body += f'{category.name} 예산 총액: {category_budget_sum}\n'

            match today_date.month:
                case 1, 3, 5, 7, 8, 10, 12:
                    month_day = 31
                case _:
                    month_day = 30

            try:
                fit_spend = int(round(category_budget_sum / month_day, -2))

                email_body += f'{category.name} 금일 적정 지출 금액: {fit_spend:,}\n'
                email_body += f'{category.name} 금일 실제 지출 금액: {category_spend_sum:,}\n'

                danger_percent = int(
                    round(category_spend_sum / fit_spend, 2) * 100
                )

                email_body += f'{category.name} 위험도: {danger_percent}%\n\n'
            except ZeroDivisionError:
                email_body += f'{category.name} 위험도: 0%\n\n'

        send_mail(
            email_subject,
            email_body,
            os.getenv('EMAIL_HOST_USER'),
            ['allen9535@naver.com']  # 테스트용
            # [user.email for user in ALL_USERS] # 실사용
        )
