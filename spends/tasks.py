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


# Celery 태스크 등록을 위한 애노테이션
@shared_task
# 오늘 사용할 예산에 대한 컨설팅 제공하는 기능
def send_messages_to_customer():
    # 이메일 제목
    email_subject = '[예산 관리 서비스] 오늘 예산에 대한 컨설팅입니다!'

    # 전체 사용자를 순회
    # range가 1부터 시작해야 하는 이유: 사용자 id가 0인 것은 없기 때문
    # for i in range(1, ALL_USERS.count() + 1): # 실사용
    for i in range(1, 2):  # 테스트용
        # 사용자 객체
        user = ALL_USERS.get(id=i)

        # 해당 사용자의 전체 예산 내역과 지출 내역
        user_budgets = Budget.objects.filter(user=user)
        user_spends = Spend.objects.filter(user=user)

        # 사용자의 가장 마지막 예산 내역
        # 꾸준히 사용하고 있다 가정했을 때, 이번달에 적용될 에산안
        last_budget = user_budgets.last()

        # 사용자의 예산안에서 이번달 예산액 총액 산출
        total_budget_sum = user_budgets.filter(
            start_at__gte=last_budget.start_at,
            end_at__lte=last_budget.end_at
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        # 사용자의 지출 내역에서 이번달 지출 총액 산출
        total_spend_sum = user_spends.filter(
            spend_at__gte=last_budget.start_at,
            spend_at__lte=last_budget.end_at
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        # 이번달 예산안에서 남은 기간동안 하루에 지출할 수 있는 금액 산출
        # 전체 예산액에서 이미 지출한 금액을 빼고 남은 기간으로 나눔
        # 그 후 10의 자리에서 반올림
        can_spend_per_last_days = int(round(
            (
                (total_budget_sum - total_spend_sum) /
                (last_budget.end_at - datetime.now().date() + timedelta(days=1)).days
            ), -2)
        )

        # 이메일 본문 생성
        email_body = ''
        # 만약 남은 기간동안의 일일 지출액이 0원 이하일 경우 최소 지출금액 10,000원 제안
        # 당 서비스는 건전한 소비 습관 정착이 목표이므로, 사용 가능한 금액을 제시해야 함
        if can_spend_per_last_days <= 0:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 전체 예산을 이미 초과하셨어요! 더 나은 소비 습관을 위해 노력합시다!\n \n \n'
        # 만약 남은 기간동안의 일일 지출액이 최소 지출 제안 금액 미만일 경우 최소 지출금액인 10,000원 제안
        # 0원 이하일 경우와의 차이점은 메시지 내용
        elif can_spend_per_last_days < 10000:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 (최소금액) 총 10,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 곧 예산을 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n \n'
        # 그 이상일 경우 여유가 있고, 적절한 소비 습관을 갖추고 있다고 판단
        else:
            email_body += f'{user.username}님의 금일 지출 가능 금액은 총 {can_spend_per_last_days:,}원\n아직 여유가 있네요! 남은 일자도 힘내세요!\n \n \n'

        # 카테고리 순회
        for category in CATEGORIES:
            # 사용자의 이번달 예산안에서 카테고리에 해당하는 예산 총액 산출
            category_budget_sum = user_budgets.filter(
                category=category.id,
                start_at__gte=last_budget.start_at,
                end_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            # 사용자의 이번달 지출 내역에서 카테고리에 해당하는 지출 총액 산출
            category_spend_sum = user_spends.filter(
                category=category.id,
                spend_at__gte=last_budget.start_at,
                spend_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            # 이번달 카테고리별 예산안에서 남은 기간동안 하루에 지출할 수 있는 금액 산출
            # 카테고리별 전체 예산액에서 이미 지출한 금액을 빼고 남은 기간으로 나눔
            # 그 후 10의 자리에서 반올림
            can_spend_per_last_days = int(round(
                (
                    (category_budget_sum - category_spend_sum) /
                    (last_budget.end_at - datetime.now().date() +
                     timedelta(days=1)).days
                ), -2)
            )

            # 이메일 본문 생성
            # 만약 남은 기간동안의 일일 지출액이 0원 이하일 경우 최소 지출금액 5,000원 제안
            # 당 서비스는 건전한 소비 습관 정착이 목표이므로, 사용 가능한 금액을 제시해야 함
            if can_spend_per_last_days <= 0:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 해당 항목에서 사용 가능한 예산을 이미 초과하셨어요! 이렇게 되면 전체 예산이 흔들리게 됩니다! 더 나은 소비 습관을 위해 노력해주세요!\n \n'
            # 만약 남은 기간동안의 일일 지출액이 최소 지출 제안 금액 미만일 경우 최소 지출금액인 5,000원 제안
            # 0원 이하일 경우와의 차이점은 메시지 내용
            elif can_spend_per_last_days < 5000:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 5,000원\n원래라면 {can_spend_per_last_days:,}원 입니다! 해당 카테고리에서 사용 가능한 예산을 곧 초과할 것 같아요! 절약이 필요한 시점입니다!\n \n'
            # 그 이상일 경우 여유가 있고, 적절한 소비 습관을 갖추고 있다고 판단
            else:
                email_body += f'금일 {category.name} 항목에서 사용 가능한 금액은 총 {can_spend_per_last_days:,}원\n예산을 잘 관리하고 계시네요! 남은 기간도 파이팅!\n \n'

            email_body += f'\n'

        # 실제로 이메일 전송
        send_mail(
            email_subject,
            email_body,
            os.getenv('EMAIL_HOST_USER'),
            ['allen9535@naver.com']  # 테스트용
            # [user.email for user in ALL_USERS] # 실사용
        )


# Celery 태스크 등록을 위한 애노테이션
@shared_task
# 오늘의 지출 내역을 관리하는 기능
def send_result_to_customer():
    # 이메일 제목
    email_subject = '[예산 관리 서비스] 오늘 지출 내역에 대한 안내입니다!'
    # 오늘 날짜를 date 형식으로
    today_date = datetime.now().date()

    # 전체 사용자를 순회
    # range가 1부터 시작해야 하는 이유: 사용자 id가 0인 것은 없기 때문
    # for i in range(ALL_USERS.count()): # 실사용
    for i in range(1, 2):  # 테스트용
        # 이메일 본문 생성
        email_body = ''

        # 사용자 객체
        user = ALL_USERS.get(id=i)

        # 해당 사용자의 전체 예산 내역과 지출 내역
        user_budgets = Budget.objects.filter(user=user)
        user_spends = Spend.objects.filter(user=user)

        # 사용자의 가장 마지막 예산 내역
        # 꾸준히 사용하고 있다 가정했을 때, 이번달에 적용될 에산안
        last_budget = user_budgets.last()

        # 사용자의 지출 내역에서 오늘 지출 총액 산출
        today_spend_sum = user_spends.filter(
            spend_at=today_date
        ).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        # 오늘 지출 총액을 이메일 본문에 추가
        email_body += f'오늘 지출한 총액: {today_spend_sum:,}원\n\n'

        # 카테고리 순회
        for category in CATEGORIES:
            # 사용자의 이번달 예산안에서 카테고리에 해당하는 예산 총액 산출
            category_budget_sum = user_budgets.filter(
                category=category,
                start_at__gte=last_budget.start_at,
                end_at__lte=last_budget.end_at
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            # 사용자의 오늘 지출 내역에서 카테고리에 해당하는 지출 총액 산출
            category_spend_sum = user_spends.filter(
                category=category,
                spend_at=today_date
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            # 카테고리별 지출 총액을 이메일 본문에 추가
            email_body += f'{category.name} 예산 총액: {category_budget_sum}\n'

            # 이번달 말일이 언제인지 산출
            match today_date.month:
                case 1, 3, 5, 7, 8, 10, 12:
                    month_day = 31
                case _:
                    month_day = 30

            # 위험도 계산 과정에서 오늘 지출 금액이 0원일 수 있음
            # ZeroDivisionError 대신 위험도를 0%로 설정하는 예외처리
            try:
                # 카테고리별 예산 총액을 일자별로 나누고
                # 10의 자리에서 반올림 한 후 정수형으로 형변환
                # -> 즉 오늘 지출해야 했을 적정 금액 산출
                fit_spend = int(round(category_budget_sum / month_day, -2))

                # 이메일 본문에 금일 적정 지출액과 실 지출액 추가
                email_body += f'{category.name} 금일 적정 지출 금액: {fit_spend:,}\n'
                email_body += f'{category.name} 금일 실제 지출 금액: {category_spend_sum:,}\n'

                # 카테고리별 지출했어야 하는 금액 대비 실지출 금액 퍼센테이지 산출
                danger_percent = int(
                    round(category_spend_sum / fit_spend, 2) * 100
                )

                # 이메일 본문에 위험도 추가
                email_body += f'{category.name} 위험도: {danger_percent}%\n\n'
            except ZeroDivisionError:
                # 위험도 계산시 오늘 지출 금액이 0원일 경우 위험도는 0%로 처리
                email_body += f'{category.name} 위험도: 0%\n\n'

        # 실제로 이메일 전송
        send_mail(
            email_subject,
            email_body,
            os.getenv('EMAIL_HOST_USER'),
            ['allen9535@naver.com']  # 테스트용
            # [user.email for user in ALL_USERS] # 실사용
        )
