from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from django.db.models.functions import Coalesce
from django.db.models import Count, Sum

from categories.models import Category
from .models import Budget
from .serializers import (
    BudgetSerializer,
    BudgetListSerializer,
    BudgetDetailSerializer
)

from datetime import datetime


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


# api/v1/budgets/create/
class BudgetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        information = request.data
        for data in information:
            category = data.get('category')
            amount = data.get('amount')
            start_at = data.get('start_at')
            end_at = data.get('end_at')

            if (category is None) or (amount is None) or (start_at is None) or (end_at is None):
                return Response(
                    {'message': '필수값(카테고리, 금액, 시작일, 종료일)을 입력해주세요.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category = get_object_or_none(Category, name=category)
            if category is None:
                return Response(
                    {'message': '유효한 카테고리명을 입력해주세요.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                amount = int(amount)
                start_at = datetime.strptime(
                    data.get('start_at'),
                    '%Y-%m-%d'
                ).date()
                end_at = datetime.strptime(
                    data.get('end_at'),
                    '%Y-%m-%d'
                ).date()
            except (ValueError, TypeError) as e:
                return Response(
                    {'message': f'유효한 값을 입력해주세요. {e}'},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )

            preprocessed_data = {
                'user': request.user.id,
                'category': category.id,
                'amount': amount,
                'start_at': start_at,
                'end_at': end_at
            }

            serializer = BudgetSerializer(data=preprocessed_data)
            if serializer.is_valid():
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

    def get(self, request):
        user = request.user

        budget_list = Budget.objects.filter(user=user)

        serializer = BudgetListSerializer(budget_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# api/v1/budgets/detail/<int:budget_no>
class BudgetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # api/v1/budgets/detail/<int:budget_no>
    def get(self, request, budget_no):
        user = request.user

        try:
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer = BudgetDetailSerializer(budget)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # api/v1/budgets/detail/<int:budget_no>/update/
    def put(self, request, budget_no):
        user = request.user

        try:
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

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
    def delete(self, request, budget_no):
        user = request.user

        try:
            budget = Budget.objects.get(user=user, id=budget_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        budget.delete()

        return Response(
            {'message': '데이터가 삭제되었습니다.'},
            status=status.HTTP_200_OK
        )


class BudgetRecommendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            total_budget = int(request.data.get('amount'))

            if total_budget <= 0:
                raise ValueError
        except ValueError as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        all_budgets = Budget.objects.all()
        categories = Category.objects.all()

        category_average = {}
        for category in categories:
            filtered_budgets = all_budgets.filter(category=category.id)

            category_count = filtered_budgets.aggregate(
                count=Coalesce(Count('category'), 0)
            ).get('count')

            category_sum = filtered_budgets.aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            category_average[category.name] = (category_sum / category_count)

        sum_category_average = sum(category_average.values())

        category_percentage = category_average.copy()
        category_percentage['others'] = 0
        for key, value in category_average.items():
            percentage = round((value / sum_category_average), 2)

            if percentage <= 0.10:
                category_percentage['others'] += percentage
                category_percentage[key] = 0
            else:
                category_percentage[key] = percentage * total_budget
        category_percentage['others'] = round(
            category_percentage.get('others'),
            2
        ) * total_budget

        return Response({'data': category_percentage}, status=status.HTTP_200_OK)
