"""Service implementing user registration flow."""
from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from account.exceptions import RegistrationConflictError, RegistrationValidationError
from account.models import User
from datastore.domains.account_dto import RegisterUserCommand, UserProfileDTO


class RegistrationService:
    """Coordinate the registration process for a new user."""

    def execute(self, command: RegisterUserCommand) -> UserProfileDTO:
        """Validate input, persist the new user, and return profile DTO."""

        self._validate_username(command.username)
        self._ensure_unique_credentials(command)

        user = self._build_user(command)
        self._validate_user(user)
        self._persist_user(user)

        return self._build_profile_dto(user)

    def _validate_username(self, username: str) -> None:
        if any(char.isspace() for char in username):
            errors = {"username": [_("Username cannot contain whitespace.")]}
            raise RegistrationValidationError(errors)

    def _ensure_unique_credentials(self, command: RegisterUserCommand) -> None:
        if User.objects.filter(username=command.username).exists():
            raise RegistrationConflictError("username", "Username already taken.")

        if User.objects.filter(email=command.email).exists():
            raise RegistrationConflictError("email", "Email already taken.")

    def _build_user(self, command: RegisterUserCommand) -> User:
        user = User(username=command.username, email=command.email)
        user.set_password(command.password)
        return user

    def _validate_user(self, user: User) -> None:
        try:
            user.full_clean()
        except DjangoValidationError as exc:
            errors = self._format_validation_errors(exc)
            raise RegistrationValidationError(errors) from exc

    def _persist_user(self, user: User) -> None:
        try:
            with transaction.atomic():
                user.save()
        except IntegrityError as exc:  # pragma: no cover - safeguards high-volume race condition
            raise RegistrationConflictError("unknown", "Account already exists.") from exc

    @staticmethod
    def _format_validation_errors(exc: DjangoValidationError) -> dict[str, list[str]]:
        errors: dict[str, list[str]] = {}
        for field, messages in exc.message_dict.items():
            errors[field] = [str(message) for message in messages]
        if not errors and exc.messages:
            errors["non_field_errors"] = [str(message) for message in exc.messages]
        return errors

    @staticmethod
    def _build_profile_dto(user: User) -> UserProfileDTO:
        return UserProfileDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
        )
