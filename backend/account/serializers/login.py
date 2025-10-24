"""Serializers for login endpoint.

LoginSerializer validates username and password fields, converting them to
LoginCommand objects for the service layer.
"""
from __future__ import annotations

from rest_framework import serializers

from datastore.domains.account_dto import LoginCommand

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class LoginSerializer(serializers.Serializer):
    """Validate login payload before handing off to service layer.

    Ensures username and password meet minimum requirements and converts
    validated data to LoginCommand for processing.
    """

    username = serializers.CharField(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        trim_whitespace=True,
        help_text="Username (case-sensitive, 3-50 characters).",
    )
    password = serializers.CharField(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        write_only=True,
        help_text="Password (8-128 characters).",
    )

    def validate(self, attrs: dict) -> dict:
        """Perform cross-field validation.

        Args:
            attrs: Dictionary of field values.

        Returns:
            Validated attributes dictionary.
        """
        # Currently no cross-field validation needed; this can be extended
        # for future requirements (e.g., checking for suspicious patterns).
        return attrs

    def to_command(self) -> LoginCommand:
        """Return validated data mapped to command object.

        Returns:
            LoginCommand with username and password.

        Raises:
            AssertionError: If serializer has not been validated yet.
        """
        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_command()."
            raise AssertionError(msg)
        return LoginCommand(**self.validated_data)
