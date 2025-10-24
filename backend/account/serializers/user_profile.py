"""Serializer for user profile output.

UserProfileSerializer converts UserProfileDTO to JSON representation for
the /auth/me endpoint response. This is a read-only serializer since the
endpoint accepts no input validation - it's a simple data retrieval operation.
"""
from __future__ import annotations

from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    """Serialize UserProfileDTO to JSON response.

    All fields are read-only since /auth/me is a GET endpoint that returns
    existing user data without accepting any input to validate.

    Fields:
    - id: User's unique identifier
    - username: User's login name
    - email: User's email address
    - created_at: ISO 8601 timestamp of account creation
    """

    MAX_USERNAME_LENGTH = 50

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        read_only=True,
        max_length=MAX_USERNAME_LENGTH,
    )
    email = serializers.EmailField(read_only=True)
    created_at = serializers.DateTimeField(
        read_only=True,
        format="iso-8601",
        help_text="Account creation timestamp in ISO 8601 format.",
    )
