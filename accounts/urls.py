from django.urls import path

from .views import SignupAPIView, EmailVerifyAPIView, LoginAPIView, LogoutAPIView


urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('verify/<str:token>', EmailVerifyAPIView.as_view(), name='email_verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout')
]
