from django.contrib import admin
from django.urls import path, include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Budget Management API",
        default_version="v1",
        description="사용자의 예산 관리를 도와주는 서비스입니다.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(
            url="https://github.com/allen9535/budget-management-project"),
    ),
    public=True,
)


urlpatterns = [
    re_path(
        "^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(r"^$", schema_view.with_ui(
        "swagger", cache_timeout=0), name="schema-root"),
    re_path(
        r"redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc-v1",
    ),

    path('admin/', admin.site.urls),

    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/categories/', include('categories.urls')),
    path('api/v1/budgets/', include('budgets.urls')),
    path('api/v1/spends/', include('spends.urls')),
]
