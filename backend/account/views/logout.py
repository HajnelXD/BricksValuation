"""API views for logout endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from account.services.logout_service import LogoutService
from config import jwt_config


class LogoutView(APIView):
    """Handle user logout via POST /api/v1/auth/logout.

    Requires authentication (IsAuthenticated permission).
    Logs the logout event and deletes the JWT cookie from client.
    """

    permission_classes = [IsAuthenticated]
    service_class = LogoutService

    def post(self, request: Request) -> Response:
        """Handle POST /api/v1/auth/logout.

        Args:
            request: Authenticated HTTP request (user set by JWT authentication).

        Returns:
            Response with 204 No Content and deleted JWT cookie.

        Notes:
            - Returns 204 No Content (no response body).
            - Deletes JWT cookie by setting Max-Age=0 and empty value.
            - Delegates logout logic to LogoutService for audit/logging.
        """
        # Delegate to service for logout logic (audit logging, etc.)
        service = self.service_class()
        service.execute(
            user_id=request.user.id,
            username=request.user.username,
        )

        # Create response with 204 No Content status
        response = Response(status=status.HTTP_204_NO_CONTENT)

        # Delete JWT cookie from client by setting empty value and Max-Age=0
        # Note: delete_cookie() in Django doesn't support all parameters, so we set
        # the cookie with httponly=True explicitly during deletion for security.
        response.set_cookie(
            key=jwt_config.COOKIE_NAME,
            value="",
            max_age=0,
            secure=jwt_config.COOKIE_SECURE,
            httponly=jwt_config.COOKIE_HTTP_ONLY,
            samesite=jwt_config.COOKIE_SAME_SITE,
            path="/",
        )

        return response
