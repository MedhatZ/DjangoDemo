from django.urls import path

from .auth_views import login_mock, me

urlpatterns = [
    path("login/", login_mock, name="auth-login"),
    path("me/", me, name="auth-me"),
]
