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

        result = self.service.execute(cmd)

        assert isinstance(result, UserRefDTO)
        assert result.id == self.active_user.id
        assert result.username == TEST_USERNAME
        assert result.email == TEST_EMAIL

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
        """Test that returned DTO excludes created_at and other sensitive fields."""
        cmd = LoginCommand(username=TEST_USERNAME, password=TEST_PASSWORD)

        result = self.service.execute(cmd)

        # UserRefDTO should not have created_at (only id, username, email)
        assert not hasattr(result, "created_at")
        assert not hasattr(result, "password")
        assert not hasattr(result, "is_active")

    def test_empty_password_raises_error(self) -> None:
        """Test that empty password raises InvalidCredentialsError."""
        cmd = LoginCommand(username=TEST_USERNAME, password="")

        with self.assertRaises(InvalidCredentialsError):
            self.service.execute(cmd)

    def test_multiple_users_login_independently(self) -> None:
        """Test that multiple users can login independently."""
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="Password1!",
        )

        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="Password2!",
        )

        cmd1 = LoginCommand(username="user1", password="Password1!")
        result1 = self.service.execute(cmd1)
        assert result1.id == user1.id

        cmd2 = LoginCommand(username="user2", password="Password2!")
        result2 = self.service.execute(cmd2)
        assert result2.id == user2.id
