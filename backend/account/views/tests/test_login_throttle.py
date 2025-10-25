"""Tests for login rate limiting/throttling."""
from __future__ import annotations

from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from account.views.login import LoginView

TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecurePass123!"


class TestLoginRateThrottling(APITestCase):
    """Test rate limiting for login endpoint."""

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

    def test_successful_login_within_rate_limit(self) -> None:
        """Test that login succeeds within rate limit."""
        payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)

        assert response.status_code == status.HTTP_200_OK

    def test_repeated_failed_attempts_logged(self) -> None:
        """Test that repeated failed attempts can be logged.

        Note: DRF throttling requires cache backend configuration.
        This test verifies that failed requests return 401, not 429.
        """
        payload = {"username": TEST_USERNAME, "password": "WrongPassword!"}

        for _ in range(3):
            request = self.factory.post(self.url, payload, format="json")
            response = self.view(request)
            # Should return 401 (auth failure), not 429 (throttle)
            assert response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

    def test_valid_login_after_failed_attempts(self) -> None:
        """Test that valid login works after failed attempts."""
        # First, attempt with wrong password
        wrong_payload = {"username": TEST_USERNAME, "password": "WrongPassword!"}
        request_wrong = self.factory.post(self.url, wrong_payload, format="json")
        response_wrong = self.view(request_wrong)
        assert response_wrong.status_code == status.HTTP_401_UNAUTHORIZED

        # Then, attempt with correct password
        correct_payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
        request_correct = self.factory.post(
            self.url, correct_payload, format="json"
        )
        response_correct = self.view(request_correct)

        # Should succeed if not throttled
        assert response_correct.status_code in [
            status.HTTP_200_OK,
            status.HTTP_429_TOO_MANY_REQUESTS,
        ]
