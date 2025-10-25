"""Service implementing BrickSet delete (DELETE) flow."""
from __future__ import annotations

from django.db import transaction
from django.contrib.auth import get_user_model

from catalog.exceptions import BrickSetNotFoundError, BrickSetEditForbiddenError
from catalog.models import BrickSet

User = get_user_model()


class DeleteBrickSetService:  # noqa: WPS338
    """Coordinate BrickSet deletion with authorization and business rule checks."""

    def execute(
        self,
        brickset_id: int,
        requesting_user: User,
    ) -> None:
        """Delete BrickSet with RB-01 rule validation.

        Flow:
        1. Fetch BrickSet by id with prefetch_related('valuations')
        2. If not found -> raise BrickSetNotFoundError
        3. Check authorization: only owner can delete (raise BrickSetEditForbiddenError)
        4. Check RB-01 business rules (identical to PATCH):
           - No valuations from other users allowed (raise BrickSetEditForbiddenError)
           - Owner's valuation must have 0 likes (raise BrickSetEditForbiddenError)
        5. Delete BrickSet in transaction.atomic() with CASCADE
        6. Return None (204 No Content response)

        Args:
            brickset_id: Primary key of the BrickSet
            requesting_user: User performing the deletion (for auth check)

        Returns:
            None (DELETE endpoint returns 204 No Content)

        Raises:
            BrickSetNotFoundError: If BrickSet with given id doesn't exist
            BrickSetEditForbiddenError: If user not owner or RB-01 rules violated
        """
        # Fetch BrickSet with related valuations
        try:
            brickset = BrickSet.bricksets.prefetch_related("valuations").get(
                pk=brickset_id,
            )
        except BrickSet.DoesNotExist as exc:
            raise BrickSetNotFoundError(brickset_id) from exc

        # Authorization: only owner can delete
        if brickset.owner_id != requesting_user.id:
            raise BrickSetEditForbiddenError("not_owner")

        # RB-01: Check business rule constraints before delete
        self._validate_delete_allowed(brickset)

        # Perform delete in transaction
        self._delete_brickset(brickset)

    @staticmethod
    def _validate_delete_allowed(brickset: BrickSet) -> None:
        """Validate RB-01 business rules: no other users' valuations or owner likes.

        RB-01: BrickSet can only be deleted if:
        - No valuations from other users exist AND
        - Owner's valuation (if exists) has 0 likes

        Args:
            brickset: BrickSet instance with prefetched valuations

        Raises:
            BrickSetEditForbiddenError: If RB-01 rules violated with specific reason
        """
        # Get all valuations (already prefetched)
        valuations = list(brickset.valuations.all())

        # Check for valuations from other users
        other_users_valuations = [
            valuation for valuation in valuations
            if valuation.user_id != brickset.owner_id
        ]
        if other_users_valuations:
            raise BrickSetEditForbiddenError("other_users_valuations_exist")

        # Check owner's valuation for likes (if exists)
        owner_valuation = next(
            (
                valuation for valuation in valuations
                if valuation.user_id == brickset.owner_id
            ),
            None,
        )
        if owner_valuation and owner_valuation.likes_count > 0:
            raise BrickSetEditForbiddenError("owner_valuation_has_likes")

    @staticmethod
    def _delete_brickset(brickset: BrickSet) -> None:
        """Delete BrickSet instance with CASCADE handling.

        Wrapped in transaction.atomic() for atomicity. CASCADE delete via Django ORM
        automatically removes related Valuations and their Likes.

        Args:
            brickset: BrickSet instance to delete
        """
        with transaction.atomic():
            brickset.delete()
