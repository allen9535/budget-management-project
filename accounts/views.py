from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.cache import cache

from dotenv import load_dotenv

from .serializers import SignupSerializer, LoginSerializer
from .models import User

import os

load_dotenv()


# api/v1/accounts/signup/
class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            link = f'http://127.0.0.1:8000/api/v1/accounts/verify/{str(refresh)}'
            email_subject = '이메일 인증을 완료해주세요.'
            email_body = (
                f'안녕하세요, {user.username}님!\n아래의 링크를 클릭하시고 이메일 인증을 완료하시면 서비스를 이용하실 수 있습니다.\n{link}'
            )

            send_mail(
                email_subject,
                email_body,
                os.getenv('EMAIL_HOST_USER'),
                [user.email]
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
    def get(self, request, token):
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token['user_id'])

            if not user.is_active:
                user.is_active = True
                user.save()
                return Response(
                    {
                        'message': '이메일 인증이 완료되었습니다. 이제 정상적으로 서비스를 이용할 수 있습니다.'
                    }, status=status.HTTP_200_OK
                )

            return Response(
                {
                    'message': '이미 인증이 완료된 계정입니다. 다시 확인해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response(
                {
                    'message': '토큰이 유효하지 않거나, 존재하지 않는 사용자입니다.'
                }, status=status.HTTP_404_NOT_FOUND
            )


# api/v1/accounts/login/
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if (username is None) or (password is None):
            return Response(
                {
                    'message': '아이디와 비밀번호를 모두 입력해주세요.'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is not None:
            serializer = LoginSerializer(user)

            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            cache.set(
                f'api/v1/accounts/login/{user.username}',
                refresh_token
            )

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
    def post(self, request):
        user = request.user
        refresh_token = cache.get(f'api/v1/accounts/login/{user.username}')
        if refresh_token is None:
            return Response(
                {
                    'message': '로그아웃할 수 없습니다.'
                }, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            cache.delete(f'api/v1/login/{user.username}')

            return Response(
                {
                    'message': '로그아웃이 완료되었습니다.'
                }, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    'message': '로그아웃 처리 중 에러가 발생했습니다.'
                }, status=status.HTTP_400_BAD_REQUEST
            )
