from django.urls import path

from .views import inventory_report

urlpatterns = [
    path("inventory", inventory_report, name="reports-inventory"),
]
