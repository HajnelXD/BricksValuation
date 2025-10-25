"""Service implementing BrickSet update (PATCH) flow."""
from __future__ import annotations

from django.db import transaction
from django.contrib.auth import get_user_model

from catalog.exceptions import BrickSetNotFoundError, BrickSetEditForbiddenError
from catalog.models import BrickSet
from datastore.domains.catalog_dto import (
    UpdateBrickSetCommand,
    BrickSetDetailDTO,
    ValuationInlineDTO,
)

User = get_user_model()


class UpdateBrickSetService:  # noqa: WPS338
    """Coordinate BrickSet partial update with authorization and business rule checks."""

    def execute(
        self,
        brickset_id: int,
        command: UpdateBrickSetCommand,
        requesting_user: User,
    ) -> BrickSetDetailDTO:
        """Update BrickSet fields with RB-01 rule validation.

        Flow:
        1. Fetch BrickSet by id with prefetch_related('valuations')
        2. If not found -> raise BrickSetNotFoundError
        3. Check authorization: only owner can edit (raise BrickSetEditForbiddenError)
        4. Check RB-01 business rules:
           - No valuations from other users allowed (raise BrickSetEditForbiddenError)
           - Owner's valuation must have 0 likes (raise BrickSetEditForbiddenError)
        5. Update allowed fields in transaction.atomic()
        6. Build and return updated BrickSetDetailDTO

        Args:
            brickset_id: Primary key of the BrickSet
            command: UpdateBrickSetCommand with fields to update (optional)
            requesting_user: User performing the update (for auth check)

        Returns:
            BrickSetDetailDTO with updated fields and all details

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

        # Authorization: only owner can edit
        if brickset.owner_id != requesting_user.id:
            raise BrickSetEditForbiddenError("not_owner")

        # RB-01: Check business rule constraints before edit
        self._validate_edit_allowed(brickset)

        # Perform update in transaction
        self._update_brickset(brickset, command)

        # Build and return updated DTO with valuations
        return self._build_detail_dto(brickset)

    @staticmethod
    def _validate_edit_allowed(brickset: BrickSet) -> None:
        """Validate RB-01 business rules: no other users' valuations or owner likes.

        RB-01: BrickSet can only be edited if:
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
    def _update_brickset(brickset: BrickSet, command: UpdateBrickSetCommand) -> None:
        """Apply command updates to BrickSet model fields.

        Only updates provided command fields (has_box, owner_initial_estimate).
        Wrapped in transaction.atomic() for atomicity.

        Args:
            brickset: BrickSet instance to update
            command: UpdateBrickSetCommand with fields to apply
        """
        update_fields = []

        # Apply conditional updates only for provided fields
        if command.has_box is not None:
            brickset.has_box = command.has_box
            update_fields.append("has_box")

        if command.owner_initial_estimate is not None:
            brickset.owner_initial_estimate = command.owner_initial_estimate
            update_fields.append("owner_initial_estimate")

        # Persist changes (updated_at auto-updated by auto_now=True on model)
        if update_fields:
            with transaction.atomic():
                brickset.save(update_fields=update_fields)

    @staticmethod
    def _build_detail_dto(brickset: BrickSet) -> BrickSetDetailDTO:
        """Map BrickSet instance to detail DTO.

        Maps valuations to DTOs and calculates aggregates (count, likes).

        Args:
            brickset: BrickSet instance with prefetched valuations

        Returns:
            BrickSetDetailDTO with all fields populated
        """
        # Map related valuations to DTOs in creation order
        valuation_dtos = [
            ValuationInlineDTO(
                id=valuation.id,
                user_id=valuation.user_id,
                value=valuation.value,
                currency=valuation.currency,
                comment=valuation.comment,
                likes_count=valuation.likes_count,
                created_at=valuation.created_at,
            )
            for valuation in brickset.valuations.all()
        ]

        # Calculate aggregates from fetched valuations
        valuations_count = len(valuation_dtos)
        total_likes = sum(valuation.likes_count for valuation in valuation_dtos)

        # Build and return detail DTO
        return BrickSetDetailDTO(
            id=brickset.id,
            number=brickset.number,
            production_status=brickset.production_status,
            completeness=brickset.completeness,
            has_instructions=brickset.has_instructions,
            has_box=brickset.has_box,
            is_factory_sealed=brickset.is_factory_sealed,
            owner_initial_estimate=brickset.owner_initial_estimate,
            owner_id=brickset.owner_id,
            valuations=valuation_dtos,
            valuations_count=valuations_count,
            total_likes=total_likes,
            created_at=brickset.created_at,
            updated_at=brickset.updated_at,
        )
