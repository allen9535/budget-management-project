from rest_framework import serializers

from budgets.models import Budget
from categories.models import Category
from accounts.models import User
from .models import Spend


class SpendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spend
        fields = '__all__'


class SpendListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Spend
        fields = [
            'user',
            'category',
            'amount',
            'memo',
            'spend_at',
            'created_at'
        ]

    def get_user(self, obj):
        spend = Spend.objects.get(id=obj.id)
        user_id = spend.user.id

        return User.objects.get(id=user_id).username

    def get_category(self, obj):
        spend = Spend.objects.get(id=obj.id)
        category_id = spend.category.id

        return Category.objects.get(id=category_id).name
