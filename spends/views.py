from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from categories.models import Category
from .models import Spend
from .serializers import SpendSerializer

from datetime import datetime


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


# api/v1/spends/list/
class SpendListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_at = request.query_params.get('start_at', None)
        end_at = request.query_params.get('end_at', None)
        category = request.query_params.get('category', None)
        min_amount = request.query_params.get('min_amount', None)
        max_amount = request.query_params.get('max_amount', None)

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
                {'message': f'유효한 값을 입력해주세요. {e}'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        if (min_amount is None) or (max_amount is None):
            if category is not None:
                try:
                    category = Category.objects.get(name=category)
                except ObjectDoesNotExist as e:
                    return Response(
                        {'message': f'유효한 값을 입력해주세요. {e}'},
                        status=status.HTTP_406_NOT_ACCEPTABLE
                    )

                spend_list = Spend.objects.filter(
                    user=request.user.id,
                    spend_at__gte=start_at,
                    spend_at__lte=end_at,
                    category=category.id
                )

                serializer = SpendSerializer(spend_list, many=True)

                return Response(
                    {'data': serializer.data},
                    status=status.HTTP_200_OK
                )

            spend_list = Spend.objects.filter(
                user=request.user.id,
                spend_at__gte=start_at,
                spend_at__lte=end_at
            )

            serializer = SpendSerializer(spend_list, many=True)

            return Response(
                {'data': serializer.data},
                status=status.HTTP_200_OK
            )

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
                user=request.user.id,
                spend_at__gte=start_at,
                spend_at__lte=end_at,
                amount__gte=min_amount,
                amount__lte=max_amount,
                category=category.id
            )

            serializer = SpendSerializer(spend_list, many=True)

            return Response(
                {'data': serializer.data},
                status=status.HTTP_200_OK
            )

        spend_list = Spend.objects.filter(
            user=request.user.id,
            spend_at__gte=start_at,
            spend_at__lte=end_at,
            amount__gte=min_amount,
            amount__lte=max_amount
        )

        serializer = SpendSerializer(spend_list, many=True)

        return Response(
            {'data': serializer.data},
            status=status.HTTP_200_OK
        )


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