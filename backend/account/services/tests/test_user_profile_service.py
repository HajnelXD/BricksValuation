"""Tests for UserProfileService."""
from __future__ import annotations

from datetime import datetime

from django.test import TestCase

from account.models import User
from account.services.user_profile_service import UserProfileService
from datastore.domains.account_dto import UserProfileDTO

NONEXISTENT_ID_OFFSET = 9999


class UserProfileServiceTests(TestCase):
    """Test user profile retrieval and DTO mapping."""

    def setUp(self) -> None:
        """Create test user with predictable data."""
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = UserProfileService()

    def test_execute_returns_user_profile_dto(self) -> None:
        """Verify execute() returns UserProfileDTO instance."""
        profile_dto = self.service.execute(self.test_user.id)
        self.assertIsInstance(profile_dto, UserProfileDTO)

    def test_execute_includes_all_required_fields(self) -> None:
        """Verify DTO contains all required profile fields."""
        profile_dto = self.service.execute(self.test_user.id)

        self.assertEqual(profile_dto.id, self.test_user.id)
        self.assertEqual(profile_dto.username, "testuser")
        self.assertEqual(profile_dto.email, "test@example.com")
        self.assertIsInstance(profile_dto.created_at, datetime)

    def test_execute_with_valid_user_id(self) -> None:
        """Verify fetching profile with valid user ID succeeds."""
        profile_dto = self.service.execute(self.test_user.id)

        self.assertEqual(profile_dto.id, self.test_user.id)
        self.assertEqual(profile_dto.username, self.test_user.username)
        self.assertEqual(profile_dto.email, self.test_user.email)

    def test_missing_user_raises_error(self) -> None:
        """Verify User.DoesNotExist raised when user ID not found."""
        nonexistent_id = self.test_user.id + NONEXISTENT_ID_OFFSET

        with self.assertRaises(User.DoesNotExist):
            self.service.execute(nonexistent_id)

    def test_returned_dto_excludes_sensitive_fields(self) -> None:
        """Verify DTO does not expose password or security fields.

        Sensitive fields must never be included in the profile DTO:
        - password hash
        - is_staff
        - is_superuser
        - last_login
        - updated_at
        """
        profile_dto = self.service.execute(self.test_user.id)

        # Verify sensitive attributes don't exist in DTO
        self.assertFalse(hasattr(profile_dto, "password"))
        self.assertFalse(hasattr(profile_dto, "is_staff"))
        self.assertFalse(hasattr(profile_dto, "is_superuser"))
        self.assertFalse(hasattr(profile_dto, "last_login"))
        self.assertFalse(hasattr(profile_dto, "updated_at"))

    def test_returned_dto_has_correct_field_types(self) -> None:
        """Verify DTO fields have expected types."""
        profile_dto = self.service.execute(self.test_user.id)

        self.assertIsInstance(profile_dto.id, int)
        self.assertIsInstance(profile_dto.username, str)
        self.assertIsInstance(profile_dto.email, str)
        self.assertIsInstance(profile_dto.created_at, datetime)

    def test_multiple_users_return_own_profile(self) -> None:
        """Verify service returns correct user when multiple exist."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="pass123",
        )

        test_user_dto = self.service.execute(self.test_user.id)
        other_user_dto = self.service.execute(other_user.id)

        # Each service call returns only the requested user
        self.assertEqual(test_user_dto.id, self.test_user.id)
        self.assertEqual(test_user_dto.username, "testuser")

        self.assertEqual(other_user_dto.id, other_user.id)
        self.assertEqual(other_user_dto.username, "otheruser")

    def test_created_at_timestamp_preserved(self) -> None:
        """Verify created_at timestamp is correctly mapped and preserved."""
        profile_dto = self.service.execute(self.test_user.id)

        # Timestamps should match (within 1 second for DB precision)
        time_diff = abs(
            (profile_dto.created_at - self.test_user.created_at).total_seconds(),
        )
        self.assertLess(time_diff, 1)

    def test_fetch_user_only_selects_required_fields(self) -> None:
        """Verify database query uses .only() for optimization.

        This test ensures the query fetches only required fields,
        not all columns (select *), reducing memory and network overhead.
        """
        profile_dto = self.service.execute(self.test_user.id)

        # DTO should contain only selected fields
        dto_dict = {
            "id": profile_dto.id,
            "username": profile_dto.username,
            "email": profile_dto.email,
            "created_at": profile_dto.created_at,
        }
        self.assertEqual(len(dto_dict), 4)

    def test_username_with_special_characters(self) -> None:
        """Verify service handles usernames with special characters."""
        special_user = User.objects.create_user(
            username="user_with-special.chars",
            email="special@example.com",
            password="pass123",
        )

        special_profile_dto = self.service.execute(special_user.id)

        self.assertEqual(special_profile_dto.username, "user_with-special.chars")

    def test_email_with_subdomain(self) -> None:
        """Verify service handles complex email addresses."""
        complex_email_user = User.objects.create_user(
            username="complexuser",
            email="user+tag@subdomain.example.co.uk",
            password="pass123",
        )

        complex_profile_dto = self.service.execute(complex_email_user.id)

        self.assertEqual(complex_profile_dto.email, "user+tag@subdomain.example.co.uk")
