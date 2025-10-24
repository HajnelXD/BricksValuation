"""Unit tests for LoginService.

Tests cover successful authentication and error scenarios.
"""
from __future__ import annotations

from django.test import TestCase

from account.exceptions import InvalidCredentialsError
from account.services.login_service import LoginService
from account.models import User
from datastore.domains.account_dto import LoginCommand, UserRefDTO

TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecurePass123!"


class LoginServiceTests(TestCase):
    """Test LoginService authentication logic."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = LoginService()
        self.active_user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
        )
        self.active_user.is_active = True
        self.active_user.save()

    def test_successful_login_returns_user_ref_dto(self) -> None:
        """Test successful login returns UserRefDTO with user data."""
        cmd = LoginCommand(username=TEST_USERNAME, password=TEST_PASSWORD)

        user_dto = self.service.execute(cmd)

        assert isinstance(user_dto, UserRefDTO)
        assert user_dto.id == self.active_user.id
        assert user_dto.username == TEST_USERNAME
        assert user_dto.email == TEST_EMAIL

    def test_nonexistent_username_raises_error(self) -> None:
        """Test that nonexistent username raises InvalidCredentialsError."""
        cmd = LoginCommand(username="nonexistent", password=TEST_PASSWORD)

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_incorrect_password_raises_error(self) -> None:
        """Test that incorrect password raises InvalidCredentialsError."""
        cmd = LoginCommand(username=TEST_USERNAME, password="WrongPassword123!")

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_inactive_user_raises_error(self) -> None:
        """Test that inactive user raises InvalidCredentialsError."""
        inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password=TEST_PASSWORD,
        )
        inactive_user.is_active = False
        inactive_user.save()

        cmd = LoginCommand(username="inactive", password=TEST_PASSWORD)

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_username_is_case_sensitive(self) -> None:
        """Test that username matching is case-sensitive."""
        cmd = LoginCommand(username=TEST_USERNAME.upper(), password=TEST_PASSWORD)

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_username_with_leading_space_fails(self) -> None:
        """Test that username with leading space fails (not trimmed here)."""
        cmd = LoginCommand(username=f" {TEST_USERNAME}", password=TEST_PASSWORD)

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_returned_dto_excludes_sensitive_data(self) -> None:
        """Test that returned DTO excludes created_at and other fields."""
        cmd = LoginCommand(username=TEST_USERNAME, password=TEST_PASSWORD)

        user_dto = self.service.execute(cmd)

        assert not hasattr(user_dto, "created_at")
        assert not hasattr(user_dto, "password")
        assert not hasattr(user_dto, "is_active")

    def test_empty_password_raises_error(self) -> None:
        """Test that empty password raises InvalidCredentialsError."""
        cmd = LoginCommand(username=TEST_USERNAME, password="")

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_multiple_users_login_independently(self) -> None:
        """Test that multiple users can login independently."""
        user_alt = User.objects.create_user(
            username="user_alt",
            email="user_alt@example.com",
            password="PasswordAlt!",
        )

        cmd_active = LoginCommand(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )
        dto_active = self.service.execute(cmd_active)
        assert dto_active.id == self.active_user.id

        cmd_alt = LoginCommand(username="user_alt", password="PasswordAlt!")
        dto_alt = self.service.execute(cmd_alt)
        assert dto_alt.id == user_alt.id
