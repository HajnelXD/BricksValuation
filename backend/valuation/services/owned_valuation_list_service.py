"""Service implementing owned Valuation listing for authenticated users.

Provides filtering by user, aggregation of likes_count, ordering by
popularity or chronology. Includes nested brickset reference in DTO.
"""
from __future__ import annotations

from django.db.models import QuerySet

from datastore.domains.valuation_dto import OwnedValuationListItemDTO
from valuation.models import Valuation


class OwnedValuationListService:  # noqa: WPS338
    """Coordinate owned Valuation listing with ordering and DTO mapping.

    Filters valuations by authenticated user, applies ordering (with validation),
    and maps to OwnedValuationListItemDTO with nested brickset reference.
    """

    ALLOWED_ORDERINGS = [
        "created_at",
        "-created_at",
        "likes_count",
        "-likes_count",
        "value",
        "-value",
    ]

    DEFAULT_ORDERING = "-created_at"

    def get_queryset(self, user_id: int, ordering: str | None = None) -> QuerySet:
        """Build and return optimized QuerySet for user's valuations.

        Flow:
        1. Filter Valuation by user_id
        2. Optimize with select_related("brickset") to avoid N+1 queries
        3. Apply ordering (with validation)

        Args:
            user_id: ID of the authenticated user (valuation owner)
            ordering: Ordering field from ALLOWED_ORDERINGS (optional)

        Returns:
            QuerySet of Valuation objects with brickset joined
        """
        queryset = Valuation.valuations.filter(user_id=user_id)

        # Optimize with select_related to prevent N+1 queries
        queryset = queryset.select_related("brickset")

        # Apply ordering with validation
        ordering = ordering or self.DEFAULT_ORDERING
        queryset = self._apply_ordering(queryset, ordering)

        return queryset

    @staticmethod
    def _apply_ordering(queryset: QuerySet, ordering: str) -> QuerySet:
        """Apply ordering by the specified field with validation.

        Args:
            queryset: Input QuerySet
            ordering: Ordering field name (must be in ALLOWED_ORDERINGS)

        Returns:
            Ordered QuerySet (unchanged if ordering invalid)
        """
        allowed_orderings = [
            "created_at",
            "-created_at",
            "likes_count",
            "-likes_count",
            "value",
            "-value",
        ]
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        return queryset

    def map_to_dto(self, valuation: Valuation) -> OwnedValuationListItemDTO:
        """Map a Valuation instance to OwnedValuationListItemDTO.

        Constructs nested brickset dict with id and number from the
        related brickset object (expected to be already fetched via
        select_related).

        Args:
            valuation: Valuation instance with brickset relation loaded

        Returns:
            OwnedValuationListItemDTO with nested brickset reference
        """
        brickset_dict = {
            "id": valuation.brickset.id,
            "number": valuation.brickset.number,
        }

        return OwnedValuationListItemDTO(
            id=valuation.id,
            brickset=brickset_dict,
            value=valuation.value,
            currency=valuation.currency,
            likes_count=valuation.likes_count,
            created_at=valuation.created_at,
        )
