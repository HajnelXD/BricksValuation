"""Tests for the RegisterUserSerializer."""
import pytest
from django.test import TestCase

from account.serializers.registration import RegisterUserSerializer

USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
PASSWORD_FIELD = "password"

USERNAME_WITH_PADDING = "  master_builder  "
TRIMMED_USERNAME = "master_builder"
VALID_EMAIL = "builder@example.com"
VALID_PASSWORD = "Secur3Pass!"
ALT_USERNAME = "builder"
ALT_PASSWORD = "ValidPass123"


class RegisterUserSerializerTests(TestCase):
    """Validate RegisterUserSerializer behavior."""

    def test_to_command_returns_register_user_command(self) -> None:
        serializer = RegisterUserSerializer(
            data={
                USERNAME_FIELD: USERNAME_WITH_PADDING,
                EMAIL_FIELD: VALID_EMAIL,
                PASSWORD_FIELD: VALID_PASSWORD,
            }
        )
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command()

        assert command.username == TRIMMED_USERNAME
        assert command.email == VALID_EMAIL
        assert command.password == VALID_PASSWORD

    def test_to_command_requires_validation(self) -> None:
        serializer = RegisterUserSerializer(
            data={
                USERNAME_FIELD: "bricklover",
                EMAIL_FIELD: "bricklover@example.com",
                PASSWORD_FIELD: VALID_PASSWORD,
            }
        )

        msg = "Serializer must be validated before calling to_command()."
        with pytest.raises(AssertionError, match=msg):
            serializer.to_command()

    def test_serializer_rejects_invalid_email(self) -> None:
        serializer = RegisterUserSerializer(
            data={
                USERNAME_FIELD: ALT_USERNAME,
                EMAIL_FIELD: "not-an-email",
                PASSWORD_FIELD: ALT_PASSWORD,
            }
        )

        is_valid = serializer.is_valid()

        assert not is_valid
        assert EMAIL_FIELD in serializer.errors

    def test_serializer_rejects_short_password(self) -> None:
        serializer = RegisterUserSerializer(
            data={
                USERNAME_FIELD: ALT_USERNAME,
                EMAIL_FIELD: VALID_EMAIL,
                PASSWORD_FIELD: "short",
            }
        )

        is_valid = serializer.is_valid()

        assert not is_valid
        assert PASSWORD_FIELD in serializer.errors
