from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.cache import cache

from drf_yasg.utils import swagger_auto_schema

from dotenv import load_dotenv

from swagger_parameters import *

from .serializers import SignupSerializer, LoginSerializer
from .models import User

import os

load_dotenv()


# api/v1/accounts/signup/
class SignupAPIView(APIView):
    @swagger_auto_schema(
        operation_id='회원가입',
        operation_description='계정명, 이메일, 휴대전화 번호, 비밀번호를 입력받아 회원가입을 진행합니다.',
        tags=['사용자', '생성'],
        request_body=SignupSerializer,
        responses={
            201: '회원가입시 입력한 이메일로 인증 메일이 발송되었습니다. 확인 후 인증을 진행해주세요.',
            400: '사용자가 입력한 값에 문제가 있을 수 있습니다. 에러 메시지를 확인해주세요.'
        }
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # 이메일 인증에 액세스 토큰을 사용
            refresh = AccessToken.for_user(user)

            # 이메일 인증 API 실행을 위해 URL에 액세스 토큰을 붙임
            link = f'http://127.0.0.1:8000/api/v1/accounts/verify/{str(refresh)}'
            # 이메일 제목
            email_subject = '이메일 인증을 완료해주세요.'
            # 이메일 본문
            email_body = (
                f'안녕하세요, {user.username}님!\n아래의 링크를 클릭하시고 이메일 인증을 완료하시면 서비스를 이용하실 수 있습니다.\n{link}'
            )

            # 실제로 이메일 전송
            send_mail(
                email_subject,
                email_body,
                os.getenv('EMAIL_HOST_USER'),   # 이메일 보내는 주소
                [user.email]                    # 이메일 받는 주소
            )

            return Response(
                {
                    'username': user.username,
                    'message': '이메일 인증을 완료하고 회원가입을 완료해주세요.'
                }, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# api/v1/accounts/verify/<str:token>
class EmailVerifyAPIView(APIView):
    @swagger_auto_schema(
        operation_id='이메일 인증',
        operation_description='회원가입을 시도한 회원이 메일의 인증 링크를 클릭하면 작동하는 API입니다. 액세스 토큰이 사용됩니다.',
        tags=['사용자'],
        responses={
            200: '이메일 인증이 완료되었습니다. 이제 정상적으로 서비스를 이용할 수 있습니다.',
            400: '이미 인증이 완료된 계정입니다.',
            404: '토큰이 유효하지 않거나 존재하지 않는 사용자입니다.'
        }
    )
    def get(self, request, token):
        try:
            # 단순 문자열이 아니라 AccessToken 타입으로 형변환
            token = AccessToken(token)
            user = User.objects.get(id=token['user_id'])

            # 이메일 인증 전에는 활성화 여부가 False
            if not user.is_active:
                # 활성화 여부를 True로 만들고 저장
                user.is_active = True
                user.save()

                return Response(
                    {
                        'message': '이메일 인증이 완료되었습니다. 이제 정상적으로 서비스를 이용할 수 있습니다.'
                    }, status=status.HTTP_200_OK
                )

            # 이미 인증이 완료된 계정의 경우
            return Response(
                {
                    'message': '이미 인증이 완료된 계정입니다. 다시 확인해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        # 토큰이 유효하지 않거나, 에러가 발생했을 때, 또는 해당하는 사용자가 없을 경우
        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response(
                {
                    'message': '토큰이 유효하지 않거나, 존재하지 않는 사용자입니다.'
                }, status=status.HTTP_404_NOT_FOUND
            )


# api/v1/accounts/login/
class LoginAPIView(APIView):
    @swagger_auto_schema(
        operation_id='로그인',
        operation_description='계정명과 비밀번호를 통해 로그인을 진행합니다.',
        tags=['사용자'],
        request_body=LoginSerializer,
        responses={
            200: '로그인에 성공했습니다. 액세스 토큰이 반환됩니다.',
            400: '계정명과 비밀번호 중 한 가지, 혹은 둘 모두 입력되지 않았습니다.',
            404: '입력한 데이터와 일치하는 사용자 정보가 없습니다. 입력값을 다시 한 번 확인해주세요.'
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # 계정명과 비밀번호는 모두 필수 입력값
        if (username is None) or (password is None):
            return Response(
                {
                    'message': '아이디와 비밀번호를 모두 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        # 만약 해당하는 사용자가 없으면 None
        user = authenticate(username=username, password=password)
        if user is not None:
            serializer = LoginSerializer(user)

            # 액세스 토큰과 리프레시 토큰을 함께 발급
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            # 리프레시 토큰의 보안과 성능을 위해 Redis에 캐시 데이터로 저장
            # 리프레시 토큰의 만료 기간과 같은 1시간(=3600초)
            cache.set(f'{access_token}', refresh_token, 3600)

            return Response(
                {
                    'message': '로그인 되었습니다.',
                    'data': serializer.data,
                    'access': access_token
                }, status=status.HTTP_200_OK
            )

        return Response(
            {
                'message': '일치하는 사용자가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND
        )


# api/v1/accounts/logout/
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='로그아웃',
        operation_description='로그아웃을 진행합니다.',
        tags=['사용자'],
        manual_parameters=[HEADER_TOKEN],
        responses={
            200: '로그아웃이 완료되었습니다.',
            400: '토큰을 처리하던 중 에러가 발생했습니다.',
            401: '인증되지 않은 사용자입니다.'
        }
    )
    def post(self, request):
        user = request.user

        # 요청 헤더의 Authorization -> Bearer <Token>
        # 스킴과 토큰 사이에는 공백이 있으므로, split 함수로 분리
        # 토큰만 가져옴
        access_token = request.headers.get('Authorization').split()[1]
        refresh_token = cache.get(f'{access_token}')

        # 리프레시 토큰이 없었을 경우
        # 인증되지 않았거나 리프레시 토큰도 만료되었거나
        # 어느쪽이던 인증이 확인되지 않음
        if refresh_token is None:
            return Response(
                {
                    'message': '로그아웃할 수 없습니다.'
                }, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # 리프레시 토큰을 단순 문자열에서 리프레시 토큰 타입으로 형변환
            token = RefreshToken(refresh_token)
            # 리프레시 토큰을 블랙리스트에 등록하여 재사용 차단
            token.blacklist()

            # 캐시 데이터에서 리프레시 토큰 삭제
            cache.delete(f'{access_token}')

            return Response(
                {
                    'message': '로그아웃이 완료되었습니다.'
                }, status=status.HTTP_200_OK
            )
        # 토큰이 유효하지 않거나 에러가 발생했을 경우
        except (InvalidToken, TokenError):
            return Response(
                {
                    'message': '로그아웃 처리 중 에러가 발생했습니다.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
