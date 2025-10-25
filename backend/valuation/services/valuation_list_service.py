"""Service implementing Valuation listing for a specific BrickSet."""
from __future__ import annotations

from django.db.models import QuerySet

from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet
from datastore.domains.valuation_dto import ValuationListItemDTO
from valuation.models import Valuation


class ValuationListService:
    """Coordinate Valuation listing for a specific BrickSet.

    Provides optimized QuerySet generation and DTO mapping for
    GET /bricksets/{brickset_id}/valuations endpoint. Ensures BrickSet
    existence before filtering valuations.
    """

    def get_queryset(self, brickset_id: int) -> QuerySet:
        """Build and return optimized QuerySet filtered by BrickSet ID.

        Flow:
        1. Verify BrickSet exists (raises BrickSetNotFoundError if not)
        2. Filter valuations by brickset_id
        3. Order by popularity (-likes_count) then chronologically (created_at)

        Args:
            brickset_id: BrickSet identifier from URL path parameter.

        Returns:
            QuerySet of Valuation objects ordered by -likes_count, created_at.

        Raises:
            BrickSetNotFoundError: When BrickSet with given ID does not exist.
        """
        self._verify_brickset_exists(brickset_id)

        queryset = Valuation.valuations.filter(
            brickset_id=brickset_id,
        ).order_by("-likes_count", "created_at")

        return queryset

    def map_to_dto(self, valuation: Valuation) -> ValuationListItemDTO:
        """Map Valuation model instance to ValuationListItemDTO.

        Extracts only fields required for list response. Excludes brickset_id
        (redundant in URL context) and updated_at (not needed in list view).

        Args:
            valuation: Valuation model instance.

        Returns:
            ValuationListItemDTO with selected fields for API response.
        """
        return ValuationListItemDTO(
            id=valuation.id,
            user_id=valuation.user_id,
            value=valuation.value,
            currency=valuation.currency,
            comment=valuation.comment,
            likes_count=valuation.likes_count,
            created_at=valuation.created_at,
        )

    def _verify_brickset_exists(self, brickset_id: int) -> None:
        """Verify that BrickSet with given ID exists.

        Args:
            brickset_id: BrickSet identifier to verify.

        Raises:
            BrickSetNotFoundError: When BrickSet does not exist.
        """
        try:
            BrickSet.bricksets.get(pk=brickset_id)
        except BrickSet.DoesNotExist:
            raise BrickSetNotFoundError(brickset_id)
