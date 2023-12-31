from django.urls import path

from .views import (
    BudgetCreateAPIView,
    BudgetListAPIView,
    BudgetDetailAPIView,
    BudgetUpdateAPIView,
    BudgetDeleteAPIView,
    BudgetRecommendAPIView
)


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
        BudgetUpdateAPIView.as_view(),
        name='budget_update'
    ),
    path(
        'detail/<int:budget_no>/delete/',
        BudgetDeleteAPIView.as_view(),
        name='budget_delete'
    ),
    path('recommend/', BudgetRecommendAPIView.as_view(), name='budget_recommend')
]
