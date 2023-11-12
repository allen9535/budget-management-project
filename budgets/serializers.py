from rest_framework import serializers

from accounts.models import User
from categories.models import Category
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'


class BudgetListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'category',
            'amount',
            'start_at',
            'end_at',
            'created_at'
        ]

    def get_category(self, obj):
        budget = Budget.objects.get(id=obj.id)
        category_id = budget.category.id

        return Category.objects.get(id=category_id).name


class BudgetDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'user',
            'category',
            'amount',
            'start_at',
            'end_at',
            'created_at'
        ]

    def get_user(self, obj):
        budget = Budget.objects.get(id=obj.id)
        user_id = budget.user.id

        return User.objects.get(id=user_id).username

    def get_category(self, obj):
        budget = Budget.objects.get(id=obj.id)
        category_id = budget.category.id

        return Category.objects.get(id=category_id).name
