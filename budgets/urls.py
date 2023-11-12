from django.urls import path

from .views import BudgetCreateAPIView, BudgetListAPIView, BudgetDetailAPIView


urlpatterns = [
    path('create/', BudgetCreateAPIView.as_view(), name='budget_create'),
    path('list/', BudgetListAPIView.as_view(), name='budget_list'),
    path(
        'detail/<int:budget_no>',
        BudgetDetailAPIView.as_view(),
        name='budget_detail'
    ),
    path(
        'detail/<int:budget_no>/update/',
        BudgetDetailAPIView.as_view(),
        name='budget_update'
    ),
    path(
        'detail/<int:budget_no>/delete/',
        BudgetDetailAPIView.as_view(),
        name='budget_delete'
    ),
]
