"""Serializers for account API endpoints."""
from __future__ import annotations

from rest_framework import serializers

from datastore.domains.account_dto import RegisterUserCommand

USERNAME_MAX_LENGTH = 50
PASSWORD_MAX_LENGTH = 128


class RegisterUserSerializer(serializers.Serializer):
    """Validate register payload before handing off to service layer."""

    username = serializers.CharField(
        min_length=3,
        max_length=USERNAME_MAX_LENGTH,
        trim_whitespace=True,
    )
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        max_length=PASSWORD_MAX_LENGTH,
        write_only=True,
    )

    def to_command(self) -> RegisterUserCommand:
        """Return validated data mapped to command object."""

        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_command()."
            raise AssertionError(msg)
        return RegisterUserCommand(**self.validated_data)
