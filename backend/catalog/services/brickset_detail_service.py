"""Service implementing BrickSet detail retrieval with valuations."""
from __future__ import annotations

from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet
from datastore.domains.catalog_dto import (
    ValuationInlineDTO,
    BrickSetDetailDTO,
)


class BrickSetDetailService:  # noqa: WPS338
    """Coordinate BrickSet detail retrieval with related valuations."""

    def execute(self, brickset_id: int) -> BrickSetDetailDTO:
        """Fetch BrickSet detail with valuations and return as DTO.

        Flow:
        1. Fetch BrickSet by id with prefetch_related('valuations')
        2. If not found -> raise BrickSetNotFoundError
        3. Map valuations to ValuationInlineDTO list
        4. Calculate aggregates: valuations_count, total_likes
        5. Build and return BrickSetDetailDTO

        Args:
            brickset_id: Primary key of the BrickSet

        Returns:
            BrickSetDetailDTO with all fields populated

        Raises:
            BrickSetNotFoundError: If BrickSet with given id doesn't exist
        """
        try:
            brickset = BrickSet.bricksets.prefetch_related("valuations").get(
                pk=brickset_id,
            )
        except BrickSet.DoesNotExist as exc:
            raise BrickSetNotFoundError(brickset_id) from exc

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
