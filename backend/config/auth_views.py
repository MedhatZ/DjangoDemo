"""Mock login endpoint — Keycloak-style placeholder."""
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_mock(request):
    """
    Accept any username/password and return the mock SSO token.
    Simulates a successful Keycloak password grant for demo UX only.
    """
    username = request.data.get("username") or "demo.analyst"
    password = request.data.get("password")
    if not password:
        return Response(
            {"detail": "password is required (any non-empty value for POC)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "access_token": settings.MOCK_AUTH_TOKEN,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "username": username,
                "email": f"{username}@example.com",
                "roles": ["analyst"],
            },
            "note": "Mock Keycloak-style token. Real SSO is out of scope for this POC.",
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(
        {
            "username": request.user.username,
            "email": getattr(request.user, "email", ""),
            "auth": "mock_keycloak",
        }
    )
