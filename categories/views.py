from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from .serializers import CategorySerializer
from .models import Category

from swagger_parameters import *


# api/v1/categories/list/
class CategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='카테고리 목록',
        operation_description='전체 카테고리 목록을 반환합니다.',
        tags=['카테고리', '목록'],
        manual_parameters=[HEADER_TOKEN],
        responses={
            200: '요청이 처리되었습니다.',
            401: '인증되지 않은 사용자입니다. 로그인 후 사용해주세요.'
        }
    )
    def get(self, request):
        # 전체 카테고리 가져옴
        categories = Category.objects.all()
        # 한번에 직렬화
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
