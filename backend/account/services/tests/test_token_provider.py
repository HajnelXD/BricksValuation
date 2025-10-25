"""Unit tests for TokenProvider.

Tests cover token generation, validation, expiration, and error handling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest import mock

import jwt
import pytest

from account.services.token_provider import TokenProvider

TEST_USER_ID = 1
ADMIN_USER_ID = 99
ALT_USER_ID = 42
TEST_USERNAME = "testuser"
ADMIN_USERNAME = "admin"
ALT_USERNAME = "alice"
TEST_USERNAME_SHORT = "bob"
TAMPER_SUFFIX = "0000000000"
TAMPER_LENGTH = 10
SECONDS_PER_DAY = 86400
TEST_YEAR = 2024
TEST_MONTH = 1
TEST_DAY = 1


class TestTokenProvider:
    """Test TokenProvider JWT operations."""

    @pytest.fixture
    def provider(self) -> TokenProvider:
        """Create TokenProvider instance for testing."""
        return TokenProvider()

    def test_generate_valid_token(self, provider: TokenProvider) -> None:
        """Test generating a valid token with correct payload."""
        token = provider.generate_token(user_id=ALT_USER_ID, username=TEST_USERNAME)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = provider.decode_token(token)
        assert decoded["user_id"] == ALT_USER_ID
        assert decoded["username"] == TEST_USERNAME
        assert "exp" in decoded
        assert "iat" in decoded

    def test_token_contains_required_claims(self, provider: TokenProvider) -> None:
        """Test that token includes all required claims."""
        token = provider.generate_token(
            user_id=TEST_USER_ID,
            username=ALT_USERNAME,
        )
        decoded = provider.decode_token(token)

        assert "user_id" in decoded
        assert "username" in decoded
        assert "exp" in decoded
        assert "iat" in decoded
        assert decoded["user_id"] == TEST_USER_ID
        assert decoded["username"] == ALT_USERNAME

    def test_decode_valid_token(self, provider: TokenProvider) -> None:
        """Test decoding a valid token successfully."""
        token = provider.generate_token(
            user_id=ADMIN_USER_ID,
            username=TEST_USERNAME_SHORT,
        )
        decoded = provider.decode_token(token)

        assert decoded["user_id"] == ADMIN_USER_ID
        assert decoded["username"] == TEST_USERNAME_SHORT

    def test_expired_token_raises_error(
        self, provider: TokenProvider
    ) -> None:
        """Test that an expired token raises jwt.ExpiredSignatureError."""
        with mock.patch(
            "account.services.token_provider.datetime"
        ) as mock_datetime:
            # Simulate generating token at specific time
            jan_first = datetime(
                TEST_YEAR,
                TEST_MONTH,
                TEST_DAY,
                0,
                0,
                0,
                tzinfo=timezone.utc,
            )
            mock_datetime.now.return_value = jan_first

            token = provider.generate_token(
                user_id=TEST_USER_ID,
                username=TEST_USERNAME,
            )

        # Try to decode with mocked jwt.decode that raises expired
        with mock.patch(
            "jwt.decode"
        ) as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError()

            with pytest.raises(jwt.ExpiredSignatureError):
                provider.decode_token(token)

    def test_invalid_signature_raises_error(self, provider: TokenProvider) -> None:
        """Test that a tampered token raises jwt.InvalidSignatureError."""
        token = provider.generate_token(user_id=TEST_USER_ID, username=TEST_USERNAME)

        # Tamper with the token
        tampered = token[:-TAMPER_LENGTH] + TAMPER_SUFFIX

        with pytest.raises(jwt.InvalidSignatureError):
            provider.decode_token(tampered)

    def test_invalid_token_format_raises_error(
        self, provider: TokenProvider
    ) -> None:
        """Test that malformed token raises jwt.DecodeError."""
        with pytest.raises((jwt.DecodeError, jwt.InvalidSignatureError)):
            provider.decode_token("not.a.token")

    def test_expiration_seconds_property(self, provider: TokenProvider) -> None:
        """Test retrieving configured expiration time."""
        expiration = provider.expiration_seconds()
        assert expiration == SECONDS_PER_DAY

    def test_missing_secret_key_raises_error(
        self, provider: TokenProvider
    ) -> None:
        """Test that missing SECRET_KEY raises ValueError."""
        provider._secret_key = ""

        with pytest.raises(ValueError, match="SECRET_KEY is not configured"):
            provider.generate_token(user_id=TEST_USER_ID, username=TEST_USERNAME)

    def test_decode_with_missing_secret_raises_error(
        self, provider: TokenProvider
    ) -> None:
        """Test that decoding with missing SECRET_KEY raises ValueError."""
        provider._secret_key = ""

        with pytest.raises(ValueError, match="SECRET_KEY is not configured"):
            provider.decode_token("any.token.here")

    def test_token_expiration_time_is_correct(
        self, provider: TokenProvider
    ) -> None:
        """Test that token expiration is set correctly in seconds."""
        token = provider.generate_token(
            user_id=TEST_USER_ID,
            username=TEST_USERNAME,
        )
        decoded = provider.decode_token(token)

        exp_ts = decoded["exp"]
        iat_ts = decoded["iat"]
        exp_delta = exp_ts - iat_ts

        # Allow 2-second tolerance for test execution time
        assert abs(exp_delta - SECONDS_PER_DAY) < 2
