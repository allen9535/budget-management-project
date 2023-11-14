from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from django.db.models.functions import Coalesce
from django.db.models import Sum, Avg

from categories.models import Category
from budgets.models import Budget
from .models import Spend
from .serializers import SpendSerializer, SpendListSerializer

from datetime import datetime
from dateutil.relativedelta import relativedelta


# api/v1/spends/create/
class SpendCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        category = request.data.get('category')
        amount = request.data.get('amount')
        memo = request.data.get('memo')
        spend_at = request.data.get('spend_at')

        if (category is None) or (amount is None) or (spend_at is None):
            return Response(
                {'message': '필수값(카테고리, 금액, 소비일)을 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            spend_data = {
                'user': user.id,
                'category': Category.objects.get(name=category).id,
                'amount': int(amount),
                'memo': memo,
                'spend_at': datetime.strptime(
                    spend_at,
                    '%Y-%m-%d'
                ).date()
            }
        except (ValueError, TypeError, ObjectDoesNotExist) as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer = SpendSerializer(data=spend_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'data': serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def make_spend_list_response_data(spend_list, exclude_spend_no, categories):
    serializer = SpendListSerializer(spend_list, many=True)

    if exclude_spend_no != []:
        try:
            for spend_no in exclude_spend_no:
                spend_list = spend_list.exclude(id=int(spend_no))
        except (ValueError, TypeError) as e:
            return Response(
                {'message': f'유효한 지출 내역을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

    spend_sum = spend_list.aggregate(
        sum=Coalesce(Sum('amount'), 0)
    ).get('sum')

    category_sum = {}
    for category in categories:
        category_sum[category.name] = spend_list.filter(
            category=category
        ).aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')

    return Response(
        {
            'list': serializer.data,
            'spend_sum': spend_sum,
            'category_sum': category_sum
        }, status=status.HTTP_200_OK
    )


# api/v1/spends/list/
class SpendListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_at = request.query_params.get('start_at', None)
        end_at = request.query_params.get('end_at', None)
        if (start_at is None) or (end_at is None):
            return Response(
                {'message': '필수값(검색 시작일, 검색 종료일)을 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_at = datetime.strptime(start_at, '%Y-%m-%d').date()
            end_at = datetime.strptime(end_at, '%Y-%m-%d').date()
        except ValueError as e:
            return Response(
                {'message': f'유효한 날짜를 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        min_amount = request.query_params.get('min_amount', None)
        max_amount = request.query_params.get('max_amount', None)
        category = request.query_params.get('category', None)
        exclude_spend_no = request.query_params.getlist('exclude', None)

        categories = Category.objects.all()

        if (min_amount is None) or (max_amount is None):
            if category is not None:
                try:
                    category = Category.objects.get(name=category)
                except ObjectDoesNotExist as e:
                    return Response(
                        {'message': f'유효한 카테고리를 입력해주세요. {e}'},
                        status=status.HTTP_406_NOT_ACCEPTABLE
                    )

                spend_list = Spend.objects.filter(
                    user=request.user,
                    spend_at__gte=start_at,
                    spend_at__lte=end_at,
                    category=category.id
                )

                response_data = make_spend_list_response_data(
                    spend_list,
                    exclude_spend_no,
                    categories
                )

                return response_data

            spend_list = Spend.objects.filter(
                user=request.user,
                spend_at__gte=start_at,
                spend_at__lte=end_at
            )

            response_data = make_spend_list_response_data(
                spend_list,
                exclude_spend_no,
                categories
            )

            return response_data

        try:
            min_amount = int(min_amount)
            max_amount = int(max_amount)
        except ValueError as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        if min_amount < 0:
            return Response(
                {'message': '최솟값은 0원 이하가 될 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if category is not None:
            try:
                category = Category.objects.get(name=category)
            except ObjectDoesNotExist as e:
                return Response(
                    {'message': f'유효한 값을 입력해주세요. {e}'},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )

            spend_list = Spend.objects.filter(
                user=request.user,
                spend_at__gte=start_at,
                spend_at__lte=end_at,
                amount__gte=min_amount,
                amount__lte=max_amount,
                category=category.id
            )

            response_data = make_spend_list_response_data(
                spend_list,
                exclude_spend_no,
                categories
            )

            return response_data

        spend_list = Spend.objects.filter(
            user=request.user.id,
            spend_at__gte=start_at,
            spend_at__lte=end_at,
            amount__gte=min_amount,
            amount__lte=max_amount
        )

        response_data = make_spend_list_response_data(
            spend_list,
            exclude_spend_no,
            categories
        )

        return response_data


# api/v1/detail/<int:spend_no>
class SpendDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # api/v1/detail/<int:spend_no>
    def get(self, request, spend_no):
        user = request.user

        try:
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer = SpendSerializer(spend)

        return Response(
            {'data': serializer.data},
            status=status.HTTP_200_OK
        )

    # api/v1/detail/<int:spend_no>/update/
    def put(self, request, spend_no):
        user = request.user

        try:
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer = SpendSerializer(spend, data=request.data, partial=True)
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

    # api/v1/detail/<int:spend_no>/delete/
    def delete(self, request, spend_no):
        user = request.user

        try:
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        spend.delete()

        return Response(
            {'message': '데이터가 삭제되었습니다.'},
            status=status.HTTP_200_OK
        )


# api/v1/spends/analytics/
class SpendAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        categories = Category.objects.all()
        spends = Spend.objects.filter(user=user)

        today = datetime.now().date()

        response_data = {}

        this_month_spend = spends.filter(
            spend_at__gte=datetime(today.year, today.month, 1).date(),
            spend_at__lte=today
        )

        last_month_spend = spends.filter(
            spend_at__gte=(
                datetime(today.year, today.month, 1).date() -
                relativedelta(months=1)
            ),
            spend_at__lte=(today - relativedelta(months=1))
        )

        this_month_spend_sum = this_month_spend.aggregate(
            sum=Coalesce(Sum('amount'), 0)).get('sum')

        last_month_spend_sum = last_month_spend.aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')

        try:
            response_data['spend_per_last_month'] = {
                'total': f'{int(round((this_month_spend_sum / last_month_spend_sum) * 100, 0))}%'
            }
        except ZeroDivisionError as e:
            response_data['spend_per_last_month'] = {
                'total': 'No Data'
            }

        for category in categories:
            this_month_category_spend_sum = this_month_spend.filter(
                category=category
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            last_month_category_spend_sum = last_month_spend.filter(
                category=category
            ).aggregate(
                sum=Coalesce(Sum('amount'), 0)
            ).get('sum')

            try:
                response_data['spend_per_last_month'][
                    category.name] = f'{int(round((this_month_category_spend_sum / last_month_category_spend_sum) * 100, 0))}%'
            except ZeroDivisionError as e:
                response_data['spend_per_last_month'][category.name] = 'No Data'

        spends_for_weekday = spends.exclude(
            spend_at=today
        )

        spends_for_weekday_sum = 0
        for spend in spends_for_weekday:
            if spend.spend_at.weekday() == today.weekday():
                spends_for_weekday_sum += spend.amount

        spends_for_today_sum = spends.filter(spend_at=today).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')
        response_data['spend_per_last_weekdays'] = f'{int((round((spends_for_today_sum / spends_for_weekday_sum) * 100, 0)))}%'

        other_user_today_spends_sum = Spend.objects.exclude(user=user).filter(
            spend_at=today
        ).aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')

        match today.month:
            case 1, 3, 5, 7, 8, 10, 12:
                month_day = 31
            case _:
                month_day = 30

        other_user_budget_per_day = Budget.objects.exclude(user=user).filter(
            start_at=datetime(today.year, today.month, 1).date(),
            end_at=datetime(today.year, today.month, month_day).date()
        ).aggregate(
            average=Avg('amount')
        ).get('average') / month_day

        other_user_percent = int(
            round((other_user_today_spends_sum /
                  other_user_budget_per_day) * 100, 0)
        )

        user_today_spends_sum = spends.filter(spend_at=today).aggregate(
            sum=Coalesce(Sum('amount'), 0)
        ).get('sum')
        user_budget_per_day = Budget.objects.filter(
            start_at=datetime(today.year, today.month, 1).date(),
            end_at=datetime(today.year, today.month, month_day).date()
        ).aggregate(
            average=Avg('amount')
        ).get('average') / month_day

        user_percent = int(
            round((user_today_spends_sum / user_budget_per_day) * 100, 0)
        )

        spend_per_other = user_percent - other_user_percent
        if spend_per_other > 0:
            spend_per_other = f'{100 + int(round(spend_per_other / other_user_percent * 100, 0))}%'
        elif spend_per_other == 0:
            spend_per_other = f'100%'
        else:
            spend_per_other = f'{100 - int(round(spend_per_other / other_user_percent * 100, 0))}%'

        try:
            response_data['spend_per_others'] = spend_per_other
        except:
            response_data['spend_per_others'] = 'No Data'

        return Response(
            {
                'data': response_data
            },
            status=status.HTTP_200_OK
        )
