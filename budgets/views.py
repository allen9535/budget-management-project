from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from categories.models import Category
from .serializers import BudgetSerializer

from datetime import datetime


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


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
                print(e)
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
