"""Service for retrieving authenticated user's profile.

Handles fetching user profile data and mapping to DTO.
"""
from __future__ import annotations

from account.models import User
from datastore.domains.account_dto import UserProfileDTO


class UserProfileService:
    """Retrieve authenticated user's complete profile."""

    def execute(self, user_id: int) -> UserProfileDTO:
        """Fetch user profile by ID and return as DTO.

        Args:
            user_id: ID of the user to fetch profile for.

        Returns:
            UserProfileDTO with id, username, email, and created_at.

        Raises:
            User.DoesNotExist: If user with given ID does not exist.
        """
        user = self._fetch_user(user_id)
        return self._build_user_profile_dto(user)

    @staticmethod
    def _fetch_user(user_id: int) -> User:
        """Fetch user from database with only required fields.

        Query optimization: only select fields needed for profile DTO
        to minimize database load and memory footprint.

        Args:
            user_id: ID of the user to fetch.

        Returns:
            User instance with id, username, email, created_at.

        Raises:
            User.DoesNotExist: If user not found.
        """
        return User.objects.only(
            "id",
            "username",
            "email",
            "created_at",
        ).get(id=user_id)

    @staticmethod
    def _build_user_profile_dto(user: User) -> UserProfileDTO:
        """Build full user profile DTO.

        Maps User model fields to UserProfileDTO, excluding sensitive fields
        like password, is_staff, is_superuser, last_login, and updated_at.

        Args:
            user: User model instance.

        Returns:
            UserProfileDTO with complete profile information.
        """
        return UserProfileDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
        )
