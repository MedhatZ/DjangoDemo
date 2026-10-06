from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LegislationViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", LegislationViewSet, basename="legislation")

urlpatterns = [
    path("", include(router.urls)),
]
