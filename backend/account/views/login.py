"""API views for login endpoint."""
from __future__ import annotations

from dataclasses import asdict

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from account.exceptions import InvalidCredentialsError
from account.serializers.login import LoginSerializer
from account.services.login_service import LoginService
from account.services.token_provider import TokenProvider
from config import jwt_config


class LoginView(APIView):
    """Handle user login via POST /api/v1/auth/login.

    Validates credentials, authenticates user, generates JWT token,
    sets HttpOnly cookie, and returns user profile.
    """

    serializer_class = LoginSerializer
    service_class = LoginService
    token_provider_class = TokenProvider

    def post(self, request: Request) -> Response:
        """Handle POST /api/v1/auth/login.

        Args:
            request: HTTP request with username and password in body.

        Returns:
            Response with 200 and user data + HttpOnly cookie on success,
            or appropriate error response (400, 401).
        """
        # Validate input
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert to command
        command = serializer.to_command()

        # Authenticate
        service = self.service_class()
        try:
            user_ref = service.execute(command)
        except InvalidCredentialsError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate token
        token_provider = self.token_provider_class()
        token = token_provider.generate_token(
            user_id=user_ref.id,
            username=user_ref.username,
        )

        # Build response
        payload = asdict(user_ref)
        response = Response(
            {"user": payload},
            status=status.HTTP_200_OK,
        )

        # Set HttpOnly secure cookie with token
        response.set_cookie(
            key=jwt_config.COOKIE_NAME,
            value=token,
            max_age=jwt_config.COOKIE_MAX_AGE,
            secure=jwt_config.COOKIE_SECURE,
            httponly=jwt_config.COOKIE_HTTP_ONLY,
            samesite=jwt_config.COOKIE_SAME_SITE,
            path="/",
        )

        return response
