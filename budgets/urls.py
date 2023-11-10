from django.urls import path

from .views import BudgetCreateAPIView


urlpatterns = [
    path('create/', BudgetCreateAPIView.as_view(), name='budget-create'),
]
