"""Service implementing Like creation flow for valuations."""
from __future__ import annotations

from django.db import IntegrityError, transaction

from datastore.domains.valuation_dto import CreateLikeCommand, LikeDTO
from valuation.exceptions import (
    LikeDuplicateError,
    LikeOwnValuationError,
    ValuationNotFoundError,
)
from valuation.models import Like, Valuation


class LikeValuationService:
    """Coordinate the creation process for a new Like on a Valuation."""

    def execute(self, command: CreateLikeCommand) -> LikeDTO:
        """Validate input, persist the new Like, and return DTO.

        Verifies that:
        1. Valuation exists
        2. User is not the author of the valuation
        3. Like does not already exist (unique constraint)

        Args:
            command: CreateLikeCommand with valuation_id and user_id

        Returns:
            LikeDTO with created like data (valuation_id, user_id, created_at)

        Raises:
            ValuationNotFoundError: If Valuation with given id does not exist
            LikeOwnValuationError: If user attempts to like their own valuation
            LikeDuplicateError: If like already exists (unique constraint violation)
        """
        valuation = self._verify_valuation_exists(command.valuation_id)
        self._verify_not_own_valuation(valuation, command.user_id)
        like = self._persist_like(command.valuation_id, command.user_id)

        return self._build_dto(like)

    def _verify_valuation_exists(self, valuation_id: int) -> Valuation:
        """Verify that Valuation with given id exists.

        Args:
            valuation_id: Primary key of Valuation to verify

        Returns:
            Valuation instance if found

        Raises:
            ValuationNotFoundError: If Valuation does not exist
        """
        try:
            return Valuation.valuations.get(pk=valuation_id)
        except Valuation.DoesNotExist as exc:
            raise ValuationNotFoundError(valuation_id) from exc

    def _verify_not_own_valuation(
        self,
        valuation: Valuation,
        user_id: int,
    ) -> None:
        """Verify that user is not the author of the valuation.

        Args:
            valuation: Valuation instance to check
            user_id: ID of user attempting to like

        Raises:
            LikeOwnValuationError: If user_id matches valuation author
        """
        if valuation.user_id == user_id:
            raise LikeOwnValuationError(valuation.id)

    def _persist_like(
        self,
        valuation_id: int,
        user_id: int,
    ) -> Like:
        """Build and persist Like to database within transaction.

        Catches IntegrityError for unique constraint violations.
        Other IntegrityError types (foreign key, check constraints) are re-raised.

        Args:
            valuation_id: ID of valuation being liked
            user_id: ID of user creating the like

        Returns:
            Saved Like instance with id and timestamps

        Raises:
            LikeDuplicateError: If uniqueness constraint is violated
            IntegrityError: For other integrity constraint violations
        """
        try:
            with transaction.atomic():
                # Use explicit valuation_id and user_id to avoid proxy object issues
                # Use default 'objects' manager (Like does not have custom manager)
                like = Like.objects.create(
                    user_id=user_id,
                    valuation_id=valuation_id,
                )
                return like
        except IntegrityError as exc:
            # Check which constraint was violated by examining error message
            error_message = str(exc).lower()
            if "like_unique_user_valuation" in error_message or "unique constraint" in error_message:
                raise LikeDuplicateError(valuation_id, user_id) from exc
            # Re-raise other integrity errors (foreign key, check constraints, etc.)
            raise

    @staticmethod
    def _build_dto(like: Like) -> LikeDTO:
        """Map Like instance to DTO with all metadata.

        Args:
            like: Saved Like instance with id and timestamps

        Returns:
            LikeDTO ready for API response
        """
        return LikeDTO(
            valuation_id=like.valuation_id,
            user_id=like.user_id,
            created_at=like.created_at,
        )
