from django.urls import path

from .views import BudgetCreateAPIView, BudgetListAPIView


urlpatterns = [
    path('create/', BudgetCreateAPIView.as_view(), name='budget_create'),
    path('list/', BudgetListAPIView.as_view(), name='budget_list'),
]
