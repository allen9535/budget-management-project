from django.urls import path

from .views import (
    SpendCreateAPIView,
    SpendListAPIView,
    SpendDetailAPIView,
    SpendUpdateAPIView,
    SpendDeleteAPIView,
    SpendAnalyticsAPIView
)


urlpatterns = [
    path('create/', SpendCreateAPIView.as_view(), name='spend_create'),
    path('list/', SpendListAPIView.as_view(), name='spend_list'),
    path('detail/<int:spend_no>', SpendDetailAPIView.as_view(), name='spend_detail'),
    path('detail/<int:spend_no>/update/',
         SpendUpdateAPIView.as_view(),
         name='spend_update'),
    path('detail/<int:spend_no>/delete/',
         SpendDeleteAPIView.as_view(),
         name='spend_delete'),

    path('analytics/', SpendAnalyticsAPIView.as_view(), name='spend_analytics'),
]
