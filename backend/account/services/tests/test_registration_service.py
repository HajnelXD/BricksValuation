"""Unit tests for the registration service."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase

from account.exceptions import RegistrationConflictError, RegistrationValidationError
from account.models import User
from account.services.registration_service import RegistrationService
from datastore.domains.account_dto import RegisterUserCommand

USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
PASSWORD_FIELD = "password"

DEFAULT_USERNAME = "new_user"
DEFAULT_EMAIL = "new_user@example.com"
DEFAULT_PASSWORD = "Secur3Pass!"
EXISTING_USERNAME = "existing"
EXISTING_EMAIL = "existing@example.com"
SECONDARY_EMAIL = "duplicate@example.com"
SECONDARY_USERNAME = "another"


def build_command(**overrides: str) -> RegisterUserCommand:
    payload = {
        USERNAME_FIELD: DEFAULT_USERNAME,
        EMAIL_FIELD: DEFAULT_EMAIL,
        PASSWORD_FIELD: DEFAULT_PASSWORD,
    }
    payload.update(overrides)
    return RegisterUserCommand(**payload)


class DummyValidationError(DjangoValidationError):
    """Provide deterministic validation error for test scenarios."""

    def __init__(self) -> None:
        super().__init__(["Non field issue."])

    @property
    def message_dict(self) -> dict[str, list[str]]:  # type: ignore[override]
        return {}


class RegistrationServiceTests(TestCase):
    """Ensure the registration service enforces domain rules."""

    def setUp(self) -> None:
        self.service = RegistrationService()

    def test_execute_creates_user_and_returns_profile(self) -> None:
        command = build_command()

        profile = self.service.execute(command)

        assert profile.username == command.username
        assert profile.email == command.email
        user = User.objects.get(pk=profile.id)
        assert user.username == command.username
        assert user.check_password(command.password)
        assert profile.created_at == user.created_at

    def test_execute_rejects_whitespace_username(self) -> None:
        command = build_command(username="invalid username")

        with pytest.raises(RegistrationValidationError) as exc:
            self.service.execute(command)

        assert USERNAME_FIELD in exc.value.errors
        assert User.objects.count() == 0

    def test_execute_conflicts_on_username(self) -> None:
        User.objects.create_user(
            username=EXISTING_USERNAME,
            email=EXISTING_EMAIL,
            password="P@ssw0rd123",
        )
        command = build_command(username=EXISTING_USERNAME, email="unique@example.com")

        with pytest.raises(RegistrationConflictError) as exc:
            self.service.execute(command)

        assert exc.value.field == USERNAME_FIELD
        assert User.objects.filter(username=EXISTING_USERNAME).count() == 1

    def test_execute_conflicts_on_email(self) -> None:
        User.objects.create_user(
            username=SECONDARY_USERNAME,
            email=SECONDARY_EMAIL,
            password="P@ssw0rd456",
        )
        command = build_command(username="unique", email=SECONDARY_EMAIL)

        with pytest.raises(RegistrationConflictError) as exc:
            self.service.execute(command)

        assert exc.value.field == EMAIL_FIELD
        assert User.objects.filter(email=SECONDARY_EMAIL).count() == 1

    def test_execute_maps_model_validation_errors(self) -> None:
        command = build_command(email="not-an-email")

        with pytest.raises(RegistrationValidationError) as exc:
            self.service.execute(command)

        assert EMAIL_FIELD in exc.value.errors
        assert User.objects.count() == 0

    def test_execute_maps_non_field_validation_errors(self) -> None:
        command = build_command()

        with patch.object(User, "full_clean", autospec=True, side_effect=DummyValidationError()):
            with pytest.raises(RegistrationValidationError) as exc:
                self.service.execute(command)

        assert "non_field_errors" in exc.value.errors
        assert exc.value.errors["non_field_errors"] == ["Non field issue."]
        assert User.objects.count() == 0
