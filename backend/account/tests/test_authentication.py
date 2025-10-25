"""Tests for JWT cookie authentication."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

import jwt

from account.authentication import JWTCookieAuthentication
from config import jwt_config

User = get_user_model()


class JWTCookieAuthenticationTests(TestCase):  # noqa: WPS338
    """Test suite for JWTCookieAuthentication."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.auth = JWTCookieAuthentication()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def _create_valid_token(self, user_id: int | None = None) -> str:
        """Create a valid JWT token for testing."""
        if user_id is None:
            user_id = self.user.id

        now = datetime.now(tz=timezone.utc)
        expiration = now + timedelta(seconds=jwt_config.EXPIRATION_SECONDS)

        payload = {
            "user_id": user_id,
            "username": "testuser",
            "exp": expiration,
            "iat": now,
        }

        return jwt.encode(
            payload,
            jwt_config.SECRET_KEY,
            algorithm=jwt_config.ALGORITHM,
        )

    def test_valid_token_returns_user_and_token(self) -> None:
        """Valid token in cookie should return (user, token)."""
        token = self._create_valid_token()
        request = self.factory.get("/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}")

        auth_result = self.auth.authenticate(request)

        assert auth_result is not None
        authenticated_user, auth_token = auth_result
        assert authenticated_user.id == self.user.id
        assert authenticated_user.username == self.user.username
        assert auth_token == token

    def test_missing_cookie_returns_none(self) -> None:
        """Request without JWT cookie should return None (allow other auth)."""
        request = self.factory.get("/")

        auth_result = self.auth.authenticate(request)

        assert auth_result is None

    def test_empty_cookie_returns_none(self) -> None:
        """Empty JWT cookie should return None."""
        request = self.factory.get("/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}=")

        auth_result = self.auth.authenticate(request)

        assert auth_result is None

    def test_invalid_token_signature_fails(self) -> None:
        """Token with invalid signature should raise AuthenticationFailed."""
        invalid_token = jwt.encode(
            {"user_id": self.user.id, "username": "testuser"},
            "wrong_secret",
            algorithm=jwt_config.ALGORITHM,
        )
        request = self.factory.get(
            "/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={invalid_token}"
        )

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_expired_token_fails(self) -> None:
        """Expired token should raise AuthenticationFailed."""
        now = datetime.now(tz=timezone.utc)
        expired_token = jwt.encode(
            {
                "user_id": self.user.id,
                "username": "testuser",
                "exp": now - timedelta(hours=1),
                "iat": now,
            },
            jwt_config.SECRET_KEY,
            algorithm=jwt_config.ALGORITHM,
        )
        request = self.factory.get(
            "/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={expired_token}"
        )

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_malformed_token_fails(self) -> None:
        """Malformed token should raise AuthenticationFailed."""
        malformed_token = "not.a.valid.jwt.token"
        request = self.factory.get(
            "/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={malformed_token}"
        )

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_user_not_found_fails(self) -> None:
        """Token with non-existent user_id should raise AuthenticationFailed."""
        nonexistent_id = 99999
        token = self._create_valid_token(user_id=nonexistent_id)
        request = self.factory.get("/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}")

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_inactive_user_fails(self) -> None:
        """Token for inactive user should raise AuthenticationFailed."""
        self.user.is_active = False
        self.user.save()

        token = self._create_valid_token()
        request = self.factory.get("/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}")

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_token_without_user_id_claim_fails(self) -> None:
        """Token missing user_id claim should raise AuthenticationFailed."""
        now = datetime.now(tz=timezone.utc)
        token = jwt.encode(
            {
                "username": "testuser",
                "exp": now + timedelta(seconds=jwt_config.EXPIRATION_SECONDS),
                "iat": now,
            },
            jwt_config.SECRET_KEY,
            algorithm=jwt_config.ALGORITHM,
        )
        request = self.factory.get("/", HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}")

        with self.assertRaisesRegex(
            AuthenticationFailed, "not valid"
        ):
            self.auth.authenticate(request)

    def test_authenticate_header_returns_bearer(self) -> None:
        """authenticate_header should return Bearer scheme."""
        request = self.factory.get("/")

        header = self.auth.authenticate_header(request)

        assert header == "Bearer"
