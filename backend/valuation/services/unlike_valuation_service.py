"""Service implementing Like deletion (DELETE) flow for valuations."""
from __future__ import annotations

from django.db import transaction

from datastore.domains.valuation_dto import UnlikeValuationCommand
from valuation.exceptions import LikeNotFoundError
from valuation.models import Like


class UnlikeValuationService:
    """Coordinate the deletion process for a Like on a Valuation."""

    def execute(self, command: UnlikeValuationCommand) -> None:
        """Validate input, remove the Like, and return None.

        Verifies that:
        1. Like exists for the given (valuation_id, user_id) pair

        Args:
            command: UnlikeValuationCommand with valuation_id and user_id

        Returns:
            None (DELETE endpoint returns 204 No Content)

        Raises:
            LikeNotFoundError: If Like for given valuation_id and user_id does not exist
        """
        self._delete_like(command.valuation_id, command.user_id)

    def _delete_like(self, valuation_id: int, user_id: int) -> None:
        """Delete Like instance with proper error handling.

        Attempts to retrieve and delete the Like. If Like.DoesNotExist is caught,
        raises domain exception LikeNotFoundError.

        Wrapped in transaction.atomic() for atomicity.

        Args:
            valuation_id: ID of valuation the like is on
            user_id: ID of user who created the like

        Raises:
            LikeNotFoundError: If Like does not exist for the given pair
        """
        try:
            like = Like.objects.get(
                valuation_id=valuation_id,
                user_id=user_id,
            )
        except Like.DoesNotExist as exc:
            raise LikeNotFoundError(valuation_id, user_id) from exc

        with transaction.atomic():
            like.delete()
