"""Unit tests for LoginSerializer.

Tests validate input sanitization, field constraints, and conversion to
LoginCommand objects.
"""
from __future__ import annotations

import pytest

from account.serializers.login import (
    LoginSerializer,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)
from datastore.domains.account_dto import LoginCommand

TEST_USERNAME = "testuser"
TEST_PASSWORD = "securepass123"
SHORT_USERNAME = "ab"
LONG_USERNAME = "a" * (USERNAME_MAX_LENGTH + 1)
SHORT_PASSWORD = "short"
LONG_PASSWORD = "a" * (PASSWORD_MAX_LENGTH + 1)
MIN_USERNAME = "a" * USERNAME_MIN_LENGTH
MAX_USERNAME = "a" * USERNAME_MAX_LENGTH
MIN_PASSWORD = "a" * PASSWORD_MIN_LENGTH
MAX_PASSWORD = "a" * PASSWORD_MAX_LENGTH


class TestLoginSerializer:
    """Test LoginSerializer validation and conversion."""

    def test_valid_data_creates_command(self) -> None:
        """Test that valid data is successfully converted to LoginCommand."""
        payload = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        }
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        command = serializer.to_command()

        assert isinstance(command, LoginCommand)
        assert command.username == TEST_USERNAME
        assert command.password == TEST_PASSWORD

    def test_missing_username_raises_validation_error(self) -> None:
        """Test that missing username field raises validation error."""
        payload = {"password": TEST_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "username" in serializer.errors
        assert "required" in str(serializer.errors["username"]).lower()

    def test_missing_password_raises_validation_error(self) -> None:
        """Test that missing password field raises validation error."""
        payload = {"username": TEST_USERNAME}
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "password" in serializer.errors
        assert "required" in str(serializer.errors["password"]).lower()

    def test_username_short_raises_error(self) -> None:
        """Test that username shorter than min length raises validation error."""
        payload = {"username": SHORT_USERNAME, "password": TEST_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "username" in serializer.errors

    def test_username_long_raises_error(self) -> None:
        """Test that username longer than max length raises validation error."""
        payload = {
            "username": LONG_USERNAME,
            "password": TEST_PASSWORD,
        }
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "username" in serializer.errors

    def test_password_short_raises_error(self) -> None:
        """Test that password shorter than min length raises validation error."""
        payload = {"username": TEST_USERNAME, "password": SHORT_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_password_long_raises_error(self) -> None:
        """Test that password longer than max length raises validation error."""
        payload = {
            "username": TEST_USERNAME,
            "password": LONG_PASSWORD,
        }
        serializer = LoginSerializer(data=payload)

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_username_whitespace_is_trimmed(self) -> None:
        """Test that leading/trailing whitespace in username is trimmed."""
        payload = {
            "username": f"  {TEST_USERNAME}  ",
            "password": TEST_PASSWORD,
        }
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["username"] == TEST_USERNAME

    def test_username_minimum_length_is_valid(self) -> None:
        """Test that username with minimum length is valid."""
        payload = {"username": MIN_USERNAME, "password": TEST_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        command = serializer.to_command()
        assert command.username == MIN_USERNAME

    def test_username_maximum_length_is_valid(self) -> None:
        """Test that username with maximum length is valid."""
        payload = {"username": MAX_USERNAME, "password": TEST_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        command = serializer.to_command()
        assert len(command.username) == USERNAME_MAX_LENGTH

    def test_password_minimum_length_is_valid(self) -> None:
        """Test that password with minimum length is valid."""
        payload = {"username": TEST_USERNAME, "password": MIN_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        command = serializer.to_command()
        assert command.password == MIN_PASSWORD

    def test_password_maximum_length_is_valid(self) -> None:
        """Test that password with maximum length is valid."""
        payload = {"username": TEST_USERNAME, "password": MAX_PASSWORD}
        serializer = LoginSerializer(data=payload)

        assert serializer.is_valid(raise_exception=True)
        command = serializer.to_command()
        assert len(command.password) == PASSWORD_MAX_LENGTH

    def test_password_is_write_only(self) -> None:
        """Test that password field is marked as write_only."""
        field = LoginSerializer().fields["password"]
        assert field.write_only is True

    def test_to_command_without_validation_raises(self) -> None:
        """Test that calling to_command() before validation raises."""
        serializer = LoginSerializer()

        with pytest.raises(AssertionError, match="must be validated"):
            serializer.to_command()

    def test_edge_case_credentials(self) -> None:
        """Test edge cases for credential validation."""
        test_cases = [
            ({"username": "", "password": TEST_PASSWORD}, False),
            ({"username": TEST_USERNAME, "password": ""}, False),
            ({"username": MIN_USERNAME, "password": MIN_PASSWORD}, True),
            ({"username": MAX_USERNAME, "password": MAX_PASSWORD}, True),
        ]

        for payload, should_be_valid in test_cases:
            serializer = LoginSerializer(data=payload)
            is_valid = serializer.is_valid()
            assert is_valid == should_be_valid
