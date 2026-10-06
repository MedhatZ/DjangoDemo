"""
Mock Keycloak-style authentication for the POC.

Production would validate JWT/OIDC via the client's existing SSO.
This placeholder accepts a fixed Bearer token so the demo can show
authenticated API access without rebuilding SSO.
"""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import authentication, exceptions


class MockUser:
    """Lightweight stand-in when Django User row is optional."""

    is_authenticated = True
    is_anonymous = False
    username = "demo.analyst"
    email = "demo.analyst@example.com"
    pk = 1
    id = 1

    def __str__(self):
        return self.username


class MockKeycloakAuthentication(authentication.BaseAuthentication):
    """
    Accepts: Authorization: Bearer <MOCK_AUTH_TOKEN>

    Placeholder for Keycloak / OIDC. Client SSO is assumed available;
    this POC does not integrate a real IdP.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        if not getattr(settings, "MOCK_AUTH_ENABLED", True):
            return None

        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            # Allow unauthenticated browse in DEBUG for convenience; views still require auth
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Invalid authorization header.")

        token = parts[1]
        expected = getattr(settings, "MOCK_AUTH_TOKEN", "poc-demo-token")
        if token != expected:
            raise exceptions.AuthenticationFailed("Invalid or expired token (mock SSO).")

        user, _ = User.objects.get_or_create(
            username="demo.analyst",
            defaults={
                "email": "demo.analyst@example.com",
                "first_name": "Demo",
                "last_name": "Analyst",
            },
        )
        return (user, {"token_type": "mock_keycloak", "sub": "demo.analyst"})

    def authenticate_header(self, request):
        return self.keyword
