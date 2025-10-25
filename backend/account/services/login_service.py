"""Service implementing user login flow.

Validates credentials, authenticates user, and returns user profile DTO.
"""
from __future__ import annotations

from account.exceptions import InvalidCredentialsError
from account.models import User
from datastore.domains.account_dto import LoginCommand, UserRefDTO


class LoginService:
    """Coordinate the login process for an existing user."""

    def execute(self, command: LoginCommand) -> UserRefDTO:
        """Authenticate user and return profile reference.

        Args:
            command: LoginCommand with username and password.

        Returns:
            UserRefDTO with user id, username, and email (no timestamps).

        Raises:
            InvalidCredentialsError: If user not found, password invalid, or inactive.
        """
        user = self._authenticate_user(command.username, command.password)
        return self._build_user_ref_dto(user)

    def _authenticate_user(self, username: str, password: str) -> User:
        """Find user and verify password.

        Args:
            username: Username to look up (case-sensitive).
            password: Password to verify.

        Returns:
            Authenticated User instance.

        Raises:
            InvalidCredentialsError: If user not found, password invalid, or inactive.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Generic message for security - don't reveal username existence
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        if not user.check_password(password):
            raise InvalidCredentialsError()

        return user

    @staticmethod
    def _build_user_ref_dto(user: User) -> UserRefDTO:
        """Build minimal user reference DTO.

        Args:
            user: User model instance.

        Returns:
            UserRefDTO with id, username, email (no created_at per spec).
        """
        return UserRefDTO(
            id=user.id,
            username=user.username,
            email=user.email,
        )
