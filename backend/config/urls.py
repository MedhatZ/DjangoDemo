from django.urls import include, path
from rest_framework.routers import DefaultRouter

from legislation.views import LegislationViewSet
from reports.views import inventory_report
from comparisons.views import ComparisonConfigViewSet, comparison_field_catalog
from config.auth_views import login_mock, me

legislation_router = DefaultRouter(trailing_slash=False)
legislation_router.register(r"legislation", LegislationViewSet, basename="legislation")

comparisons_router = DefaultRouter(trailing_slash=False)
comparisons_router.register(r"comparisons", ComparisonConfigViewSet, basename="comparisons")

urlpatterns = [
    path("api/auth/login/", login_mock, name="auth-login"),
    path("api/auth/me/", me, name="auth-me"),
    path("api/reports/inventory", inventory_report, name="reports-inventory"),
    path("api/comparisons/fields", comparison_field_catalog, name="comparison-fields"),
    path("api/", include(legislation_router.urls)),
    path("api/", include(comparisons_router.urls)),
]
