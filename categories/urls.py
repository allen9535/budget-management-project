from django.urls import path

from .views import CategoryListAPIView


urlpatterns = [
    path('list/', CategoryListAPIView.as_view(), name='category_list')
]
