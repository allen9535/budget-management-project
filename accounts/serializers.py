from rest_framework import serializers

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    check_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'password',
            'check_password'
        ]

    def create(self, validated_data):
        username = validated_data.get('username')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError()

        password = validated_data.pop('password')
        check_password = validated_data.pop('check_password')

        if password != check_password:
            raise serializers.ValidationError()

        return User.objects.create_user(**validated_data, password=password)


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone'
        ]