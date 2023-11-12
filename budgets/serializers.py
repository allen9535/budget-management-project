from rest_framework import serializers

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
