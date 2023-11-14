from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from django.db.models.functions import Coalesce
from django.db.models import Count, Sum

from drf_yasg.utils import swagger_auto_schema

from categories.models import Category
from .models import Budget
from .serializers import (
    BudgetSerializer,
    BudgetListSerializer,
    BudgetDetailSerializer
)

from swagger_parameters import *

from datetime import datetime


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


# api/v1/budgets/create/
class BudgetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='예산 생성',
        operation_description='시작일, 종료일, 카테고리, 금액을 입력받아 새 예산을 생성합니다.',
        tags=['예산', '생성'],
        manual_parameters=[HEADER_TOKEN],
        request_body=BudgetSerializer,
        responses={
            201: '성공적으로 데이터 생성이 완료되었습니다.',
            400: '입력한 값에 문제가 있습니다. 에러 메시지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def post(self, request):
        start_at = request.data.get('start_at')
        end_at = request.data.get('end_at')
        budgets_data = request.data.get('budgets')

        # 시작일, 종료일, (카테고리, 금액)은 필수값
        if (start_at is None) or (end_at is None) or (budgets_data is None):
            return Response(
                {'message': '필수값(카테고리, 금액, 시작일, 종료일)을 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 날짜를 date 형식으로 변환
        # 올바른 형식이 아닐 경우를 대비한 예외 처리
        try:
            start_at = datetime.strptime(start_at, '%Y-%m-%d').date()
            end_at = datetime.strptime(end_at, '%Y-%m-%d').date()
        except ValueError as e:
            return Response(
                {'message': f'올바른 날짜 형식이 아닙니다. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # budgets_data가 받게 될 형식은 다음과 같다:
        # {
        #     'start_at': 'YYYY-MM-DD',
        #     'end_at': 'YYYY-MM-DD',
        #     'budgets': {
        #         'house': 100000
        #     }
        # }
        # 즉 budgets_data는 딕셔너리 형태인 것
        # 같은 시작일과 종료일에 여러 카테고리와 예산액을 입력해야 하므로
        # 아래와 같이 순회하면서 저장
        for category, amount in budgets_data.items():
            # 잘못된 카테고리명이나 금액을 입력했을 경우를 대비한 예외 처리
            try:
                # 입력된 카테고리명으로 객체 가져옴
                category_obj = Category.objects.get(name=category)
                # 혹시 모르니 정수로 형변환
                amount = int(amount)
            except (ObjectDoesNotExist, ValueError) as e:
                return Response(
                    {'message': f'유효한 카테고리명, 또는 금액을 입력해주세요. {e}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            preprocessed_data = {
                'user': request.user.id,
                'category': category_obj.id,
                'amount': amount,
                'start_at': start_at,
                'end_at': end_at
            }

            serializer = BudgetSerializer(data=preprocessed_data)

            # 유효성 검사
            if serializer.is_valid():
                # 유효한 데이터이면 저장
                serializer.save()
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'message': '데이터 저장을 완료했습니다.'},
            status=status.HTTP_201_CREATED
        )


# api/v1/budgets/list/
class BudgetListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='예산 목록',
        operation_description='현재 로그인한 회원의 전체 예산 목록을 제공합니다.',
        tags=['예산', '목록'],
        manual_parameters=[HEADER_TOKEN],
        responses={
            200: '요청이 처리되었습니다.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def get(self, request):
        user = request.user

        # 현재 로그인한 사용자의 모든 예산 목록 가져옴
        budget_list = Budget.objects.filter(user=user)
        # 한번에 직렬화
        serializer = BudgetListSerializer(budget_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# api/v1/budgets/detail/<int:budget_no>
class BudgetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='예산 상세보기',
        operation_description='현재 로그인한 회원의 특정 예산 데이터를 상세하게 제공합니다.',
        tags=['예산', '상세'],
        manual_parameters=[PATH_BUDGET_NO, HEADER_TOKEN],
        responses={
            200: '요청이 처리되었습니다.',
            400: '잘못된 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 상세보기 할 예산의 ID를 포함
    def get(self, request, budget_no):
        user = request.user

        # URL에 포함된 예산 ID가 잘못되었거나, 타인의 예산 ID일 경우를 대비한 예외 처리
        try:
            # 로그인한 사용자의 예산이면서, 동시에 예산 ID를 만족해야 함
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BudgetDetailSerializer(budget)

        return Response(serializer.data, status=status.HTTP_200_OK)


# api/v1/budgets/detail/<int:budget_no>/update/
class BudgetUpdateAPIView(APIView):
    @swagger_auto_schema(
        operation_id='예산 수정',
        operation_description='현재 로그인한 회원의 특정 예산 데이터를 수정합니다.',
        tags=['예산', '수정'],
        manual_parameters=[PATH_BUDGET_NO, HEADER_TOKEN],
        request_body=BudgetSerializer,
        responses={
            200: '데이터 수정이 완료되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 수정할 예산의 ID를 포함해야 함
    def put(self, request, budget_no):
        user = request.user

        # URL에 포함된 예산 ID가 잘못되었거나, 타인의 예산 ID일 경우를 대비한 예외 처리
        try:
            # 로그인한 사용자의 예산이면서, 동시에 예산 ID를 만족해야 함
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 수정된 데이터의 유효성 검사
        # partial=True 옵션을 통해 모든 값이 입력되지 않아도 됨
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {'data': serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': '데이터 수정에 실패했습니다. 입력값을 확인해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )


# api/v1/budgets/detail/<int:budget_no>/delete/
class BudgetDeleteAPIView(APIView):
    @swagger_auto_schema(
        operation_id='예산 삭제',
        operation_description='현재 로그인한 회원의 특정 예산 데이터를 삭제합니다.',
        tags=['예산', '삭제'],
        manual_parameters=[PATH_BUDGET_NO, HEADER_TOKEN],
        responses={
            200: '데이터 삭제가 완료되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 수정할 예산의 ID를 포함해야 함
    def delete(self, request, budget_no):
        user = request.user

        # URL에 포함된 예산 ID가 잘못되었거나, 타인의 예산 ID일 경우를 대비한 예외 처리
        try:
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 데이터 삭제
        budget.delete()

        return Response(
            {'message': '데이터가 삭제되었습니다.'},
            status=status.HTTP_200_OK
        )


# api/v1/budgets/recommend/
class BudgetRecommendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='예산 추천',
        operation_description='사용자가 예산 총액을 입력하면, 타 사용자의 데이터 통계를 활용하여 카테고리별 예산 분배를 추천합니다.',
        tags=['예산', '통계'],
        manual_parameters=[HEADER_TOKEN],
        responses={
            200: '요청이 처리되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def post(self, request):
        # 예산 총액이 숫자로 변환이 불가능하거나, 0 이하인 경우 예외처리
        try:
            total_budget = int(request.data.get('amount'))

            if total_budget <= 0:
                raise ValueError
        except ValueError as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 전체 예산 내용과 카테고리를 가져옴
        all_budgets = Budget.objects.all()
        categories = Category.objects.all()

        # 카테고리별 평균 금액 산출
        category_average = {}
        # 전체 카테고리를 순서대로 순회
        for category in categories:
            # 전체 예산에서 카테고리에 해당하는 내용만 필터링
            filtered_budgets = all_budgets.filter(category=category)

            # 카테고리에 해당하는 데이터 갯수
            # 평균을 구하는 것이므로, 아래 코드와 합쳐 Avg 기능 사용하면 됨
            # 리팩토링 필요!
            category_count = filtered_budgets.aggregate(
                count=Coalesce(Count('category'), 0)
            ).get('count')

            # 카테고리에 해당하는 예산 총합
            category_sum = filtered_budgets.aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            # 카테고리 이름을 키로, 카테고리 예산 평균값을 값으로
            category_average[category.name] = (category_sum / category_count)

        # 카테고리 예산 평균값의 합
        sum_category_average = sum(category_average.values())

        # 카테고리별 평균값 딕셔너리를 복사
        category_percentage = category_average.copy()
        # 10%가 못되는 카테고리들을 합칠 others 키 값 생성
        category_percentage['others'] = 0
        # 더이상 값이 변할 일이 없는 카테고리별 평균값 딕셔너리로 순회
        for key, value in category_average.items():
            # 전체 금액 평균 대비 카테고리 평균값을 구하고 소수 셋째 자리에서 반올림
            percentage = round((value / sum_category_average), 2)

            # 퍼센테이지가 10% 이하면 기타 항목으로 합침
            if percentage <= 0.1:
                category_percentage['others'] += percentage
                # 해당하는 카테고리 퍼센테이지는 0으로
                category_percentage[key] = 0
            else:
                # 퍼센테이지가 10%를 넘으면 사용자가 입력한 총 예산에 곱해
                # 해당 카테고리 추천 예산액 산정
                category_percentage[key] = int(percentage * total_budget)

        # 기타 항목을 소수 셋째 자리에서 반올림한 다음
        # 사용자가 입력한 총 예산을 곱함
        category_percentage['others'] = int(round(
            category_percentage.get('others'), 2
        ) * total_budget)

        return Response({'data': category_percentage}, status=status.HTTP_200_OK)
