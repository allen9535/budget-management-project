from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


PHONE_NUMBER_REGEX = RegexValidator(
    regex=r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})',
    message='휴대전화 양식을 입력해주세요.'
)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        normalized_email = self.normalize_email(email)
        datetime_now = timezone.now()

        user = self.model(
            username=username,
            email=normalized_email,
            date_joined=datetime_now,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=32, unique=True, verbose_name='계정명')
    email = models.EmailField(max_length=320, unique=True, verbose_name='이메일')
    phone = models.CharField(
        validators=[PHONE_NUMBER_REGEX], max_length=13, verbose_name='휴대전화번호')
    is_active = models.BooleanField(default=False, verbose_name='활성화 여부')
    is_staff = models.BooleanField(default=False, verbose_name='스태프 여부')
    is_superuser = models.BooleanField(default=False, verbose_name='슈퍼유저 여부')
    date_joined = models.DateTimeField(auto_now=True, verbose_name='가입일')
    last_login = models.DateTimeField(
        auto_now_add=True,
        verbose_name='마지막 로그인'
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
