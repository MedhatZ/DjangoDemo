from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ComparisonConfigViewSet, comparison_field_catalog

router = DefaultRouter(trailing_slash=False)
router.register(r"comparisons", ComparisonConfigViewSet, basename="comparisons")

urlpatterns = [
    path("comparisons/fields", comparison_field_catalog, name="comparison-fields"),
    *router.urls,
]
