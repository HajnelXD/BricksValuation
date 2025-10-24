"""Custom exceptions for account domain operations."""
from __future__ import annotations

from collections.abc import Mapping


class RegistrationConflictError(Exception):
    """Raised when username or email is already taken."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.message = message


class RegistrationValidationError(Exception):
    """Raised when data fails model validation before persistence."""

    def __init__(self, errors: Mapping[str, list[str]]) -> None:
        super().__init__("Invalid registration data.")
        self.errors = errors


class LoginValidationError(Exception):
    """Raised when login data fails validation before authentication."""

    def __init__(self, errors: Mapping[str, list[str]]) -> None:
        super().__init__("Invalid login data.")
        self.errors = errors


class InvalidCredentialsError(Exception):
    """Raised when username/password combination is invalid or account inactive."""

    def __init__(self, message: str = "Invalid username or password.") -> None:
        super().__init__(message)
        self.message = message
