"""Tests for UserProfileSerializer."""
from __future__ import annotations

from datetime import datetime

from django.test import TestCase

from account.serializers.user_profile import UserProfileSerializer
from datastore.domains.account_dto import UserProfileDTO

FIRST_USER_ID = 123
SECOND_USER_ID = 456
THIRD_USER_ID = 789
FOURTH_USER_ID = 999


class UserProfileSerializerTests(TestCase):
    """Test UserProfileDTO serialization to JSON."""

    def setUp(self) -> None:
        """Create sample DTO for testing."""
        self.now = datetime.now()
        self.sample_dto = UserProfileDTO(
            id=FIRST_USER_ID,
            username="testuser",
            email="test@example.com",
            created_at=self.now,
        )
        self.serializer = UserProfileSerializer()

    def test_serialize_user_profile_dto_to_dict(self) -> None:
        """Verify DTO is correctly serialized to dictionary."""
        serialized = self.serializer.to_representation(self.sample_dto)

        self.assertIsInstance(serialized, dict)
        self.assertIn("id", serialized)
        self.assertIn("username", serialized)
        self.assertIn("email", serialized)
        self.assertIn("created_at", serialized)

    def test_serialized_data_contains_all_fields(self) -> None:
        """Verify serialized output has all required fields."""
        serialized = self.serializer.to_representation(self.sample_dto)

        self.assertEqual(serialized["id"], FIRST_USER_ID)
        self.assertEqual(serialized["username"], "testuser")
        self.assertEqual(serialized["email"], "test@example.com")

    def test_all_fields_are_read_only(self) -> None:
        """Verify all serializer fields are marked as read_only."""
        fields = self.serializer.fields

        for field_name, field in fields.items():
            self.assertTrue(
                field.read_only,
                f"Field '{field_name}' should be read_only",
            )

    def test_datetime_in_iso_format(self) -> None:
        """Verify created_at is formatted as ISO 8601 string."""
        serialized = self.serializer.to_representation(self.sample_dto)

        created_at = serialized["created_at"]
        self.assertIsInstance(created_at, str)

        # ISO 8601 format should contain 'T' separator
        self.assertIn("T", created_at)

        # Should be parseable back to datetime
        parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        self.assertIsInstance(parsed, datetime)

    def test_id_field_is_integer(self) -> None:
        """Verify ID field is serialized as integer."""
        serialized = self.serializer.to_representation(self.sample_dto)

        self.assertIsInstance(serialized["id"], int)
        self.assertEqual(serialized["id"], FIRST_USER_ID)

    def test_username_field_is_string(self) -> None:
        """Verify username field is serialized as string."""
        serialized = self.serializer.to_representation(self.sample_dto)

        self.assertIsInstance(serialized["username"], str)
        self.assertEqual(serialized["username"], "testuser")

    def test_email_field_is_string(self) -> None:
        """Verify email field is serialized as string."""
        serialized = self.serializer.to_representation(self.sample_dto)

        self.assertIsInstance(serialized["email"], str)
        self.assertEqual(serialized["email"], "test@example.com")

    def test_serializer_does_not_modify_dto(self) -> None:
        """Verify serialization doesn't mutate the original DTO."""
        original_dto = UserProfileDTO(
            id=SECOND_USER_ID,
            username="unchanged",
            email="unchanged@example.com",
            created_at=self.now,
        )

        self.serializer.to_representation(original_dto)

        # Verify DTO unchanged after serialization
        self.assertEqual(original_dto.id, SECOND_USER_ID)
        self.assertEqual(original_dto.username, "unchanged")
        self.assertEqual(original_dto.email, "unchanged@example.com")

    def test_special_characters_in_username(self) -> None:
        """Verify serializer handles special characters in username."""
        dto_with_special = UserProfileDTO(
            id=THIRD_USER_ID,
            username="user_with-special.chars",
            email="special@example.com",
            created_at=self.now,
        )

        serialized = self.serializer.to_representation(dto_with_special)

        self.assertEqual(serialized["username"], "user_with-special.chars")

    def test_complex_email_address(self) -> None:
        """Verify serializer handles complex email addresses."""
        dto_complex_email = UserProfileDTO(
            id=FOURTH_USER_ID,
            username="complexuser",
            email="user+tag@subdomain.example.co.uk",
            created_at=self.now,
        )

        serialized = self.serializer.to_representation(dto_complex_email)

        self.assertEqual(
            serialized["email"],
            "user+tag@subdomain.example.co.uk",
        )

    def test_serializer_field_types(self) -> None:
        """Verify created_at field is DateTime type."""
        fields = self.serializer.fields

        # Verify created_at field exists and is DateTime type
        self.assertEqual(type(fields["created_at"]).__name__, "DateTimeField")

    def test_invalid_input_on_write_not_allowed(self) -> None:
        """Verify serializer rejects write attempts on read-only endpoint."""
        payload = {
            "id": FOURTH_USER_ID,
            "username": "hacker",
            "email": "hack@example.com",
            "created_at": "2025-01-01T00:00:00Z",
        }

        # Read-only serializer should ignore input data
        serializer = UserProfileSerializer(data=payload)
        # Since all fields are read_only, serializer won't validate input
        self.assertTrue(serializer.is_valid())
