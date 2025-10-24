"""API integration tests for login endpoint.

Tests cover successful login, validation errors, and authentication failures.
"""
from __future__ import annotations

from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from account.views.login import LoginView
from config import jwt_config

TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecurePass123!"


class TestLoginView(APITestCase):
    """Test LoginView API endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.view = LoginView.as_view()
        self.url = reverse_lazy("auth-login")
        self.user = baker.make(
            "account.User",
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            is_active=True,
        )
        self.user.set_password(TEST_PASSWORD)
        self.user.save()

    def test_successful_login_returns_200_with_user_data(self) -> None:
        """Test successful login returns 200 with user info."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert "user" in data
        assert data["user"]["id"] == self.user.id
        assert data["user"]["username"] == TEST_USERNAME
        assert data["user"]["email"] == TEST_EMAIL

    def test_successful_login_sets_httponly_cookie(self) -> None:
        """Test that successful login sets HttpOnly cookie with token."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)

        assert response.status_code == status.HTTP_200_OK
        assert jwt_config.COOKIE_NAME in response.cookies
        cookie = response.cookies[jwt_config.COOKIE_NAME]
        assert cookie["httponly"] is True

    def test_cookie_has_correct_attributes(self) -> None:
        """Test that cookie has correct SameSite and path."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)

        assert response.status_code == status.HTTP_200_OK
        cookie = response.cookies[jwt_config.COOKIE_NAME]
        assert cookie["httponly"] is True
        assert cookie["samesite"] == jwt_config.COOKIE_SAME_SITE
        assert cookie["path"] == "/"

    def test_response_body_excludes_token(self) -> None:
        """Test that response body does not contain JWT token."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert "token" not in data
        assert "jwt" not in data

    def test_missing_username_returns_400(self) -> None:
        """Test that missing username returns 400."""
        payload = {"password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.data
        assert "errors" in data
        assert "username" in data["errors"]

    def test_missing_password_returns_400(self) -> None:
        """Test that missing password returns 400."""
        payload = {"username": TEST_USERNAME}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.data
        assert "errors" in data
        assert "password" in data["errors"]

    def test_username_too_short_returns_400(self) -> None:
        """Test that username shorter than min length returns 400."""
        payload = {"username": "ab", "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_too_short_returns_400(self) -> None:
        """Test that password shorter than min length returns 400."""
        payload = {"username": TEST_USERNAME, "password": "short"}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_credentials_returns_401(self) -> None:
        """Test that invalid credentials return 401."""
        payload = {"username": TEST_USERNAME, "password": "WrongPassword!"}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.data
        assert "detail" in data

    def test_nonexistent_user_returns_401(self) -> None:
        """Test that nonexistent user returns 401."""
        payload = {"username": "nonexistent", "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_inactive_user_returns_401(self) -> None:
        """Test that inactive user returns 401."""
        inactive_user = baker.make(
            "account.User",
            username="inactive",
            email="inactive@example.com",
            is_active=False,
        )
        inactive_user.set_password(TEST_PASSWORD)
        inactive_user.save()

        payload = {"username": "inactive", "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_message_generic_for_security(self) -> None:
        """Test that error messages are generic for both nonexistent and wrong password."""
        payload_nonexistent = {"username": "nonexistent", "password": TEST_PASSWORD}
        payload_wrong_password = {
            "username": TEST_USERNAME,
            "password": "WrongPassword!",
        }

        request_nonexistent = self.factory.post(
            self.url, payload_nonexistent, format="json"
        )
        response_nonexistent = self.view(request_nonexistent)
        response_nonexistent.render()

        request_wrong = self.factory.post(
            self.url, payload_wrong_password, format="json"
        )
        response_wrong = self.view(request_wrong)
        response_wrong.render()

        assert response_nonexistent.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_wrong.status_code == status.HTTP_401_UNAUTHORIZED

    def test_username_case_sensitivity(self) -> None:
        """Test that username is case-sensitive."""
        payload = {"username": TEST_USERNAME.upper(), "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_whitespace_in_username_trimmed_by_serializer(self) -> None:
        """Test that whitespace in username is trimmed."""
        payload = {
            "username": f"  {TEST_USERNAME}  ",
            "password": TEST_PASSWORD,
        }

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data["user"]["username"] == TEST_USERNAME

    def test_response_includes_required_user_fields(self) -> None:
        """Test that response includes id, username, and email."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data["user"]
        assert "id" in user_data
        assert "username" in user_data
        assert "email" in user_data
        assert "created_at" not in user_data
        assert "updated_at" not in user_data
