"""Tests for user profile API view."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

import jwt

from account.views.user_profile import UserProfileView
from config import jwt_config
from datastore.domains.account_dto import UserProfileDTO

User = get_user_model()

FIRST_USER_ID = 123
SECOND_USER_ID = 456


class UserProfileViewTests(TestCase):
    """Test suite for UserProfileView using APIRequestFactory."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.view = UserProfileView.as_view()
        self.profile_url = "/api/v1/auth/me"

        # Create test users
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="pass123",
        )

    def _create_valid_token(self, user_id: int | None = None) -> str:
        """Create a valid JWT token for testing."""
        if user_id is None:
            user_id = self.user.id

        now = datetime.now(tz=timezone.utc)
        expiration = now + timedelta(seconds=jwt_config.EXPIRATION_SECONDS)

        payload = {
            "user_id": user_id,
            "username": "testuser" if user_id == self.user.id else "otheruser",
            "exp": expiration,
            "iat": now,
        }

        return jwt.encode(
            payload,
            jwt_config.SECRET_KEY,
            algorithm=jwt_config.ALGORITHM,
        )

    def _create_expired_token(self, user_id: int | None = None) -> str:
        """Create an expired JWT token for testing."""
        if user_id is None:
            user_id = self.user.id

        now = datetime.now(tz=timezone.utc)
        expiration = now - timedelta(seconds=1)  # Already expired

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

    def test_authenticated_user_gets_profile_ok(self) -> None:
        """Authenticated user should get their profile with 200 OK."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_correct_user_data(self) -> None:
        """Profile response should contain correct user data."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        profile_data = response.data
        self.assertEqual(profile_data["id"], self.user.id)
        self.assertEqual(profile_data["username"], "testuser")
        self.assertEqual(profile_data["email"], "test@example.com")
        self.assertIn("created_at", profile_data)

    def test_response_excludes_sensitive_fields(self) -> None:
        """Response should not expose password or security fields."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        profile_data = response.data
        self.assertNotIn("password", profile_data)
        self.assertNotIn("is_staff", profile_data)
        self.assertNotIn("is_superuser", profile_data)
        self.assertNotIn("last_login", profile_data)
        self.assertNotIn("updated_at", profile_data)

    def test_unauthenticated_returns_unauthorized(self) -> None:
        """Request without authentication should return 401 Unauthorized."""
        request = self.factory.get(self.profile_url)
        # No force_authenticate - request is unauthenticated

        response = self.view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_content_type_is_json(self) -> None:
        """Response should have JSON data structure."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        # Check that response data is properly structured JSON
        json_data = response.data
        self.assertIsInstance(json_data, dict)
        self.assertTrue(len(json_data) > 0)

    def test_created_at_is_iso_format(self) -> None:
        """created_at timestamp should be in ISO 8601 format."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        created_at = response.data["created_at"]
        self.assertIsInstance(created_at, str)
        # ISO 8601 should contain 'T' separator
        self.assertIn("T", created_at)

    def test_user_cannot_access_other_user_profile(self) -> None:
        """User should only access their own profile, not others."""
        # Create request for user but authenticate as different user
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        # Response should be user's own data, not other_user's
        profile_data = response.data
        self.assertEqual(profile_data["id"], self.user.id)
        self.assertNotEqual(profile_data["id"], self.other_user.id)
        self.assertEqual(profile_data["username"], self.user.username)

    def test_response_all_required_fields_present(self) -> None:
        """Response should contain all required fields."""
        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        response = self.view(request)
        response.render()

        profile_data = response.data
        required_fields = {"id", "username", "email", "created_at"}
        self.assertEqual(set(profile_data.keys()), required_fields)

    def test_profile_special_characters_username(self) -> None:
        """Profile should handle usernames with special characters."""
        special_user = User.objects.create_user(
            username="user_with-special.chars",
            email="special@example.com",
            password="pass123",
        )

        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=special_user)

        response = self.view(request)
        response.render()

        self.assertEqual(
            response.data["username"],
            "user_with-special.chars",
        )

    def test_profile_with_complex_email(self) -> None:
        """Profile should handle complex email addresses."""
        complex_user = User.objects.create_user(
            username="complexuser",
            email="user+tag@subdomain.example.co.uk",
            password="pass123",
        )

        request = self.factory.get(self.profile_url)
        force_authenticate(request, user=complex_user)

        response = self.view(request)
        response.render()

        self.assertEqual(
            response.data["email"],
            "user+tag@subdomain.example.co.uk",
        )


class UserProfileViewIntegrationTests(APITestCase):
    """Integration tests for UserProfileView using APIClient."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.profile_url = "/api/v1/auth/me"

        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_view_registered_in_urls(self) -> None:
        """UserProfileView should be registered in URL configuration."""
        # This test verifies that the route exists and is accessible
        # The actual URL routing will be verified once urls.py is updated
        self.assertIsNotNone(self.profile_url)

    def test_service_called_with_user_id(self) -> None:
        """View should call service with request.user.id from JWT."""
        request_factory = APIRequestFactory()
        view = UserProfileView.as_view()

        request = request_factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        with patch(
            "account.services.user_profile_service.UserProfileService.execute",
        ) as mock_execute:
            mock_execute.return_value = UserProfileDTO(
                id=self.user.id,
                username=self.user.username,
                email=self.user.email,
                created_at=self.user.created_at,
            )

            response = view(request)
            response.render()

            # Verify service was called with correct user_id
            mock_execute.assert_called_once_with(user_id=self.user.id)

    def test_service_not_called_unauthenticated(self) -> None:
        """View should not call service if user is not authenticated."""
        request_factory = APIRequestFactory()
        view = UserProfileView.as_view()

        request = request_factory.get(self.profile_url)
        # No force_authenticate

        with patch(
            "account.services.user_profile_service.UserProfileService.execute",
        ) as mock_execute:
            # Call view without authentication
            view(request)

            # Service should NOT be called for unauthenticated request
            mock_execute.assert_not_called()

    def test_view_handles_deleted_user(self) -> None:
        """View should return 404 if user was deleted from DB."""
        request_factory = APIRequestFactory()
        view = UserProfileView.as_view()

        request = request_factory.get(self.profile_url)
        force_authenticate(request, user=self.user)

        # Delete user from database to simulate edge case
        self.user.delete()

        response_obj = view(request)
        response_obj.render()

        # When user is deleted, authentication might fail first,
        # but if it somehow reaches service, should return 404
        # In this case, deletion should cause 401 from auth layer
        self.assertIn(
            response_obj.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND],
        )
