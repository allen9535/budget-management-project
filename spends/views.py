from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from django.db.models.functions import Coalesce
from django.db.models import Sum, Avg

from drf_yasg.utils import swagger_auto_schema

from categories.models import Category
from budgets.models import Budget
from .models import Spend
from .serializers import SpendSerializer, SpendListSerializer

from swagger_parameters import *

from datetime import datetime
from dateutil.relativedelta import relativedelta


# api/v1/spends/create/
class SpendCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='지출 기록 생성',
        operation_description='현재 로그인한 사용자의 지출 기록을 생성합니다.',
        tags=['지출', '생성'],
        manual_parameters=[HEADER_TOKEN],
        request_body=SpendSerializer,
        responses={
            201: '성공적으로 데이터 생성이 완료되었습니다.',
            400: '입력한 값에 문제가 있습니다. 에러 메시지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def post(self, request):
        user = request.user
        category = request.data.get('category')
        amount = request.data.get('amount')
        memo = request.data.get('memo')
        spend_at = request.data.get('spend_at')

        # 카테고리, 금액, 지출일은 필수값
        if (category is None) or (amount is None) or (spend_at is None):
            return Response(
                {'message': '필수값(카테고리, 금액, 소비일)을 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 정확한 카테고리명, 정수형으로 변환할 수 있는 지출액,
        # date 타입으로 변환할 수 있는 지출일 값이 아닐 경우를 대비한 예외처리
        try:
            spend_data = {
                'user': user.id,
                'category': Category.objects.get(name=category).id,
                'amount': int(amount),
                'memo': memo,
                # str -> datetime -> date 형변환
                'spend_at': datetime.strptime(
                    spend_at,
                    '%Y-%m-%d'
                ).date()
            }
        except (ValueError, TypeError, ObjectDoesNotExist) as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SpendSerializer(data=spend_data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {'data': serializer.data},
                status=status.HTTP_201_CREATED
            )

        # 값이 잘못되었을 경우 유효성 검사를 통과하지 못함
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 지출 내역에 대한 응답 메시지를 생성하는 함수
# 지출 내역 쿼리셋, 제외할 지출 내역 ID 리스트, 카테고리 쿼리셋을 입력받아야 함
def make_spend_list_response_data(spend_list, exclude_spend_no, categories):
    serializer = SpendListSerializer(spend_list, many=True)

    # 만약 제외할 지출 내역이 있다면
    if exclude_spend_no != []:
        # 잘못된 지출 내역 ID가 들어있을 경우를 대비한 예외처리
        try:
            # 지출 내역 리스트를 순회하면서 지출 내역 쿼리셋에서 제외시킴
            for spend_no in exclude_spend_no:
                spend_list = spend_list.exclude(id=int(spend_no))
        except (ValueError, TypeError) as e:
            return Response(
                {'message': f'유효한 지출 내역을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # 지출 내역 쿼리셋의 금액 합계
    spend_sum = spend_list.aggregate(
        sum=Coalesce(Sum('amount'), 0)
    ).get('sum')

    # 카테고리별 금액 합계
    category_sum = {}
    # 카테고리 쿼리셋을 순회하면서 금액 합계를 구함
    for category in categories:
        category_sum[category.name] = spend_list.filter(
            category=category
        ).aggregate(sum=Coalesce(Sum('amount'), 0)).get('sum')

    # 위에서 나온 데이터들을 Response로 묶어서 반환
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

    @swagger_auto_schema(
        operation_id='지출 목록',
        operation_description='현재 로그인한 사용자의 지출 목록을 제공합니다.',
        tags=['지출', '목록'],
        manual_parameters=[
            HEADER_TOKEN, QUERY_START_AT, QUERY_END_AT,
            QUERY_MIN_AMOUNT, QUERY_MAX_AMOUNT, QUERY_CATEGORY, QUERY_EXCLUDE
        ],
        responses={
            200: '요청이 처리되었습니다.',
            400: '입력한 값에 문제가 있습니다. 에러 메시지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def get(self, request):
        # URL의 쿼리 파라미터
        start_at = request.query_params.get('start_at', None)
        end_at = request.query_params.get('end_at', None)

        # 검색 시작일과 종료일은 필수값
        if (start_at is None) or (end_at is None):
            return Response(
                {'message': '필수값(검색 시작일, 검색 종료일)을 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 검색 시작일과 종료일이 date 타입으로 형변환 불가능할 경우를 대비한 예외처리
        try:
            # str -> datetime -> date
            start_at = datetime.strptime(start_at, '%Y-%m-%d').date()
            end_at = datetime.strptime(end_at, '%Y-%m-%d').date()
        except ValueError as e:
            return Response(
                {'message': f'유효한 날짜를 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # URL의 쿼리 파라미터
        min_amount = request.query_params.get('min_amount', None)
        max_amount = request.query_params.get('max_amount', None)
        category = request.query_params.get('category', None)
        exclude_spend_no = request.query_params.getlist('exclude', None)

        # 전체 카테고리
        categories = Category.objects.all()

        # 최솟값이나 최댓값 둘 중 하나라도 없는 경우
        # -> 최솟값 최댓값 검색 안함
        if (min_amount is None) or (max_amount is None):
            # 카테고리 값이 있을 경우
            if category is not None:
                # 존재하지 않는 카테고리명을 입력했을 경우를 대비한 예외처리
                try:
                    category = Category.objects.get(name=category)
                except ObjectDoesNotExist as e:
                    return Response(
                        {'message': f'유효한 카테고리를 입력해주세요. {e}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 현재 로그인한 사용자, 카테고리,
                # 검색 시작일 <= 지출일 <= 검색 종료일
                # 조건에 해당하는 쿼리셋
                spend_list = Spend.objects.filter(
                    user=request.user,
                    spend_at__gte=start_at,
                    spend_at__lte=end_at,
                    category=category.id
                )

                # 지출 내역에 대한 응답 메시지를 생성하는 함수 호출
                # Response 타입을 반환받음
                response_data = make_spend_list_response_data(
                    spend_list,
                    exclude_spend_no,
                    categories
                )

                # 적용된 검색 조건: 검색 시작일, 종료일, 카테고리
                return response_data

            # 현재 로그인한 사용자,
            # 검색 시작일 <= 지출일 <= 검색 종료일
            # 조건에 해당하는 쿼리셋
            spend_list = Spend.objects.filter(
                user=request.user,
                spend_at__gte=start_at,
                spend_at__lte=end_at
            )

            # 지출 내역에 대한 응답 메시지를 생성하는 함수 호출
            # Response 타입을 반환받음
            response_data = make_spend_list_response_data(
                spend_list,
                exclude_spend_no,
                categories
            )

            # 적용된 검색 조건: 검색 시작일, 종료일
            return response_data

        # 최솟값과 최댓값이 모두 입력되었을 경우
        # 정수형으로 형변환 되지 않을 경우를 대비한 예외처리
        try:
            min_amount = int(min_amount)
            max_amount = int(max_amount)
        except ValueError as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 최솟값이 0 미만인 경우
        if min_amount < 0:
            return Response(
                {'message': '최솟값은 0원 이하가 될 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 최솟값, 최댓값 O / 카테고리 O
        # 카테고리 값이 있을 경우
        if category is not None:
            # 존재하지 않는 카테고리명을 입력했을 경우를 대비한 예외처리
            try:
                category = Category.objects.get(name=category)
            except ObjectDoesNotExist as e:
                return Response(
                    {'message': f'유효한 값을 입력해주세요. {e}'},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )

            # 현재 로그인한 사용자, 카테고리
            # 검색 시작일 <= 지출일 <= 검색 종료일
            # 최솟값 <= 지출액 <= 최댓값
            # 조건에 해당하는 쿼리셋
            spend_list = Spend.objects.filter(
                user=request.user,
                spend_at__gte=start_at,
                spend_at__lte=end_at,
                amount__gte=min_amount,
                amount__lte=max_amount,
                category=category.id
            )

            # 지출 내역에 대한 응답 메시지를 생성하는 함수 호출
            # Response 타입을 반환받음
            response_data = make_spend_list_response_data(
                spend_list,
                exclude_spend_no,
                categories
            )

            # 적용된 검색 조건: 검색 시작일, 종료일, 카테고리, 최솟값, 최댓값
            return response_data

        # 카테고리 X

        # 현재 로그인한 사용자,
        # 검색 시작일 <= 지출일 <= 검색 종료일
        # 최솟값 <= 지출액 <= 최댓값
        # 조건에 해당하는 쿼리셋
        spend_list = Spend.objects.filter(
            user=request.user.id,
            spend_at__gte=start_at,
            spend_at__lte=end_at,
            amount__gte=min_amount,
            amount__lte=max_amount
        )

        # 지출 내역에 대한 응답 메시지를 생성하는 함수 호출
        # Response 타입을 반환받음
        response_data = make_spend_list_response_data(
            spend_list,
            exclude_spend_no,
            categories
        )

        # 적용된 검색 조건: 검색 시작일, 종료일, 최솟값, 최댓값
        return response_data


# api/v1/detail/<int:spend_no>
class SpendDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='지출 상세보기',
        operation_description='현재 로그인한 회원의 특정 지출 데이터를 상세하게 제공합니다.',
        tags=['지출', '상세'],
        manual_parameters=[HEADER_TOKEN, PATH_SPEND_NO],
        responses={
            200: '요청이 처리되었습니다.',
            400: '잘못된 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 상세보기 할 지출 내역의 ID를 포함
    def get(self, request, spend_no):
        user = request.user

        # URL에 포함된 지출 내역 ID가 잘못되었거나, 타인의 지출 내역 ID일 경우를 대비한 예외처리
        try:
            # 로그인한 사용자의 지출 내역이면서, 동시에 지출 내역 ID를 만족해야 함
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SpendSerializer(spend)

        return Response(
            {'data': serializer.data},
            status=status.HTTP_200_OK
        )


# api/v1/detail/<int:spend_no>/update/
class SpendUpdateAPIView(APIView):
    @swagger_auto_schema(
        operation_id='지출 내역 수정',
        operation_description='현재 로그인한 회원의 특정 지출 데이터를 수정합니다.',
        tags=['지출', '수정'],
        manual_parameters=[HEADER_TOKEN, PATH_SPEND_NO],
        responses={
            200: '데이터 수정이 완료되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 수정할 지출 내역 ID를 포함해야 함
    def put(self, request, spend_no):
        user = request.user

        # URL에 포함된 지출 내역 ID가 잘못되었거나, 타인의 것일 경우를 대비한 예외 처리
        try:
            # 로그인한 사용자의 지출 내역이면서, 동시에 지출 내역 ID를 만족해야 함
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        # 수정된 데이터의 유효성 검사
        # partial=True 옵션을 통해 모든 값이 입력되지 않아도 됨
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
class SpendDeleteAPIView(APIView):
    @swagger_auto_schema(
        operation_id='지출 내역 삭제',
        operation_description='현재 로그인한 회원의 특정 지출 데이터를 삭제합니다.',
        tags=['지출', '삭제'],
        manual_parameters=[HEADER_TOKEN, PATH_SPEND_NO],
        responses={
            200: '데이터 삭제가 완료되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    # URL에 수정할 예산의 ID를 포함해야 함
    def delete(self, request, spend_no):
        user = request.user

        # URL에 포함된 지출 내역 ID가 잘못되었거나, 타인의 것일 경우를 대비한 예외 처리
        try:
            # 로그인한 사용자의 지출 내역이면서, 동시에 지출 내역 ID를 만족해야 함
            spend = Spend.objects.get(user=user.id, id=spend_no)
        except ObjectDoesNotExist as e:
            return Response(
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 데이터 삭제
        spend.delete()

        return Response(
            {'message': '데이터가 삭제되었습니다.'},
            status=status.HTTP_200_OK
        )


# api/v1/spends/analytics/
class SpendAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='지출 통계',
        operation_description='지출과 관련된 여러 통계를 제공합니다.',
        tags=['지출', '통계'],
        manual_parameters=[HEADER_TOKEN],
        responses={
            200: '요청이 처리되었습니다.',
            400: '유효하지 않은 값이 입력되었습니다. 에러 메세지를 확인해주세요.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
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

        other_user_today_spends_average = Spend.objects.exclude(user=user).filter(
            spend_at=today
        ).aggregate(average=Avg('amount')).get('average')

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
            round((other_user_today_spends_average /
                  other_user_budget_per_day) * 100, 0)
        )

        user_today_spends_average = spends.filter(spend_at=today).aggregate(
            average=Avg('amount')
        ).get('average')

        user_budget_per_day = Budget.objects.filter(
            start_at=datetime(today.year, today.month, 1).date(),
            end_at=datetime(today.year, today.month, month_day).date()
        ).aggregate(
            average=Avg('amount')
        ).get('average') / month_day

        user_percent = int(
            round((user_today_spends_average / user_budget_per_day) * 100, 0)
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
