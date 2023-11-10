from rest_framework import serializers

from .models import Spend


class SpendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spend
        fields = '__all__'
