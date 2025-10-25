"""Tests for logout API view."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

import jwt

from account.services.logout_service import LogoutService
from account.views.logout import LogoutView
from config import jwt_config

User = get_user_model()


class LogoutViewTests(TestCase):  # noqa: WPS338
    """Test suite for LogoutView using APIRequestFactory for unit-level testing."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.view = LogoutView.as_view()
        self.logout_url = "/api/v1/auth/logout"

        # Create test user
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

    def test_successful_logout_returns_no_content(self) -> None:
        """Successful logout should return no content status."""
        token = self._create_valid_token()
        request = self.factory.post(
            self.logout_url,
            HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}",
        )
        force_authenticate(request, user=self.user)

        response = self.view(request)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_response_body_is_empty(self) -> None:
        """No content response should have no body after rendering."""
        token = self._create_valid_token()
        request = self.factory.post(
            self.logout_url,
            HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}",
        )
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        assert response.content == b""

    @patch.object(LogoutService, "execute")
    def test_service_execute_called_with_user_details(
        self, mock_execute,  # type: ignore[no-untyped-def]
    ) -> None:
        """Service execute should be called with user credentials."""
        token = self._create_valid_token()
        request = self.factory.post(
            self.logout_url,
            HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}",
        )
        force_authenticate(request, user=self.user)

        self.view(request)

        assert mock_execute.call_count == 1
        call_kwargs = mock_execute.call_args[1]
        assert call_kwargs["user_id"] == self.user.id
        assert call_kwargs["username"] == self.user.username

    def test_successful_logout_flow(self) -> None:
        """Full logout flow: authenticate, logout, verify response."""
        token = self._create_valid_token()
        request = self.factory.post(
            self.logout_url,
            HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}",
        )
        force_authenticate(request, user=self.user)

        response = self.view(request)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        response.render()
        assert response.content == b""

    def test_multiple_logouts_are_independent(self) -> None:
        """Multiple logouts from same user should work independently."""
        tokens_and_responses = []
        for _ in range(2):
            token = self._create_valid_token()
            request = self.factory.post(
                self.logout_url,
                HTTP_COOKIE=f"{jwt_config.COOKIE_NAME}={token}",
            )
            force_authenticate(request, user=self.user)
            response = self.view(request)
            tokens_and_responses.append((token, response))

        for token, response in tokens_and_responses:
            assert response.status_code == status.HTTP_204_NO_CONTENT


class LogoutViewIntegrationTests(APITestCase):  # noqa: WPS338
    """Integration tests for LogoutView using REST client (tests cookies)."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create test user
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

    def test_unauth_user_returns_error(self) -> None:
        """Integration test: Unauthenticated request returns 401."""
        response = self.client.post("/api/v1/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
