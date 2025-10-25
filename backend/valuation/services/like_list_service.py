"""Service implementing Like listing for a specific Valuation."""
from __future__ import annotations

from django.db.models import QuerySet

from datastore.domains.valuation_dto import LikeListItemDTO
from valuation.exceptions import ValuationNotFoundError
from valuation.models import Like, Valuation


class LikeListService:
    """Coordinate Like listing for a specific Valuation.

    Provides optimized QuerySet generation and DTO mapping for
    GET /valuations/{valuation_id}/likes endpoint. Ensures Valuation
    existence before filtering likes.
    """

    def get_queryset(self, valuation_id: int) -> QuerySet:
        """Build and return optimized QuerySet filtered by Valuation ID.

        Flow:
        1. Verify Valuation exists (raises ValuationNotFoundError if not)
        2. Filter likes by valuation_id
        3. Order chronologically by creation timestamp (newest first)

        Args:
            valuation_id: Valuation identifier from URL path parameter.

        Returns:
            QuerySet of Like objects ordered by -created_at (newest first).

        Raises:
            ValuationNotFoundError: When Valuation with given ID does not exist.
        """
        self._verify_valuation_exists(valuation_id)

        queryset = Like.objects.filter(
            valuation_id=valuation_id,
        ).order_by("-created_at")

        return queryset

    def map_to_dto(self, like: Like) -> LikeListItemDTO:
        """Map Like model instance to LikeListItemDTO.

        Extracts only fields required for list response. Excludes valuation_id
        (redundant in URL context) and updated_at (not needed in list view).
        Includes only minimal user reference (user_id) for privacy.

        Args:
            like: Like model instance.

        Returns:
            LikeListItemDTO with selected fields for API response.
        """
        return LikeListItemDTO(
            user_id=like.user_id,
            created_at=like.created_at,
        )

    def _verify_valuation_exists(self, valuation_id: int) -> None:
        """Verify that Valuation with given ID exists.

        Args:
            valuation_id: Valuation identifier to verify.

        Raises:
            ValuationNotFoundError: When Valuation does not exist.
        """
        try:
            Valuation.valuations.get(pk=valuation_id)
        except Valuation.DoesNotExist:
            raise ValuationNotFoundError(valuation_id)
