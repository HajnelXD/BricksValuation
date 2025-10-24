"""JWT authentication class for DRF.

Extracts JWT token from cookie and validates it. Integrates with DRF's
authentication system to provide automatic request.user and request.auth.
"""
from __future__ import annotations

import logging
from typing import Any

import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from account.services.token_provider import TokenProvider
from config import jwt_config

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTCookieAuthentication(BaseAuthentication):  # noqa: WPS338
    """Authenticate requests using JWT token stored in HttpOnly cookie.

    Extracts token from `jwt_token` cookie, validates signature and expiration,
    and loads associated user. Used as DRF DEFAULT_AUTHENTICATION_CLASSES.
    """

    def __init__(self) -> None:
        """Initialize authentication with TokenProvider."""
        self.token_provider = TokenProvider()

    def authenticate(self, request: Any) -> tuple[User, str] | None:
        """Extract and validate JWT from cookie.

        Args:
            request: DRF Request object.

        Returns:
            Tuple of (user, token) if valid token found in cookie,
            None if no cookie present (allows other auth methods).

        Raises:
            AuthenticationFailed: If token is invalid, expired, or user not found.
        """
        # Try to extract token from cookie
        token = request.COOKIES.get(jwt_config.COOKIE_NAME)

        if not token:
            # No cookie - allow other auth methods or anonymous access
            return None

        try:  # noqa: WPS229
            user = self._validate_and_load_user(token)
            return (user, token)
        except (jwt.InvalidTokenError, ValueError, User.DoesNotExist):
            msg = "Given token not valid for any token type"
            raise AuthenticationFailed(msg) from None

    def _validate_and_load_user(self, token: str) -> User:  # noqa: WPS338
        """Validate token and load associated user.

        Args:
            token: JWT token string.

        Returns:
            User instance associated with token.

        Raises:
            jwt.InvalidTokenError: If token signature/format invalid.
            ValueError: If token payload invalid or user inactive.
            User.DoesNotExist: If user not found.
        """
        payload = self.token_provider.decode_token(token)

        user_id = payload.get("user_id")
        if not user_id:
            msg = "Token payload missing user_id"
            raise ValueError(msg)

        user = User.objects.get(id=user_id)

        if not user.is_active:
            msg = "User account is disabled"
            raise ValueError(msg)

        return user

    def authenticate_header(self, request: Any) -> str:
        """Return header for 401 response."""
        return "Bearer"
