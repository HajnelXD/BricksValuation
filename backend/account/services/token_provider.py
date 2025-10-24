"""JWT token generation and validation.

This module provides the TokenProvider class for generating signed JWT tokens
and decoding/validating them. Tokens are used for stateless authentication.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from config import jwt_config


class TokenProvider:
    """Generate and validate JWT tokens for authentication."""

    def __init__(self) -> None:
        """Initialize TokenProvider with configuration."""
        self._secret_key = jwt_config.SECRET_KEY
        self._algorithm = jwt_config.ALGORITHM
        self._expiration_seconds = jwt_config.EXPIRATION_SECONDS

    def generate_token(self, user_id: int, username: str) -> str:
        """Generate a signed JWT token for the given user.

        Args:
            user_id: Unique user identifier.
            username: User's username.

        Returns:
            Encoded JWT token as string.

        Raises:
            ValueError: If SECRET_KEY is not configured.
        """
        if not self._secret_key:
            msg = "JWT SECRET_KEY is not configured."
            raise ValueError(msg)

        now = datetime.now(tz=timezone.utc)
        expiration = now + timedelta(seconds=self._expiration_seconds)

        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expiration,
            "iat": now,
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.

        Args:
            token: Encoded JWT token string.

        Returns:
            Decoded payload as dictionary.

        Raises:
            jwt.InvalidTokenError: If token is invalid, expired, or signature fails.
        """
        if not self._secret_key:
            msg = "JWT SECRET_KEY is not configured."
            raise ValueError(msg)

        return jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )

    def expiration_seconds(self) -> int:
        """Return token expiration time in seconds."""
        return self._expiration_seconds
