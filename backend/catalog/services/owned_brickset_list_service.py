"""Service implementing owned BrickSet listing for authenticated users.

Provides filtering by owner, aggregations (valuations_count, total_likes),
and ordering. Includes RB-01 business rule evaluation for editable flag.
"""
from __future__ import annotations

from django.db.models import (
    Count,
    IntegerField,
    QuerySet,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from catalog.models import BrickSet
from datastore.domains.catalog_dto import OwnedBrickSetListItemDTO


class OwnedBrickSetListService:  # noqa: WPS338
    """Coordinate owned BrickSet listing with aggregations, ordering, and RB-01 logic."""

    ALLOWED_ORDERINGS = [
        "created_at",
        "-created_at",
        "valuations_count",
        "-valuations_count",
        "total_likes",
        "-total_likes",
    ]

    DEFAULT_ORDERING = "-created_at"

    def get_queryset(self, user_id: int, ordering: str | None = None) -> QuerySet:
        """Build and return optimized QuerySet for owned bricksets with annotations.

        Flow:
        1. Filter BrickSet by owner_id (user_id)
        2. Add count annotations (valuations_count, total_likes)
        3. Apply ordering (with validation)

        Args:
            user_id: ID of the authenticated user (owner)
            ordering: Ordering field from ALLOWED_ORDERINGS (optional)

        Returns:
            Annotated QuerySet with valuations_count and total_likes
        """
        queryset = BrickSet.bricksets.filter(owner_id=user_id)

        # Add aggregations
        queryset = self._add_aggregations(queryset)

        # Apply ordering with validation
        ordering = ordering or self.DEFAULT_ORDERING
        queryset = self._apply_ordering(queryset, ordering)

        return queryset

    @staticmethod
    def _add_aggregations(queryset: QuerySet) -> QuerySet:
        """Add annotations for valuations_count and total_likes.

        Optimizations:
        - valuations_count: Count('valuations', distinct=True)
        - total_likes: Coalesce(Sum('valuations__likes_count'), 0)
          to handle no valuations gracefully

        Args:
            queryset: Input QuerySet

        Returns:
            Annotated QuerySet
        """
        queryset = queryset.annotate(
            valuations_count=Count("valuations", distinct=True),
            total_likes=Coalesce(
                Sum("valuations__likes_count", output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        return queryset

    def _apply_ordering(self, queryset: QuerySet, ordering: str) -> QuerySet:
        """Apply ordering by the specified field with validation.

        Args:
            queryset: Input QuerySet
            ordering: Ordering field name (must be in ALLOWED_ORDERINGS)

        Returns:
            Ordered QuerySet
        """
        if ordering in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(ordering)
        return queryset

    def map_to_dto(self, brickset: BrickSet) -> OwnedBrickSetListItemDTO:
        """Map a BrickSet instance to OwnedBrickSetListItemDTO.

        Evaluates RB-01 business rule to determine if brickset is editable.
        Expects the queryset to have been annotated with valuations_count
        and total_likes.

        Args:
            brickset: BrickSet instance (must have valuations prefetched or
                     be retrieved from annotated queryset for prefetch)

        Returns:
            OwnedBrickSetListItemDTO with editable flag (RB-01 evaluated)
        """
        # Get aggregation counts (with fallback for non-annotated instances)
        valuations_count = getattr(brickset, "valuations_count", 0) or 0
        total_likes = getattr(brickset, "total_likes", 0) or 0

        # Evaluate RB-01 rule for editable flag
        editable = self._is_editable(brickset)

        return OwnedBrickSetListItemDTO(
            id=brickset.id,
            number=brickset.number,
            production_status=brickset.production_status,
            completeness=brickset.completeness,
            valuations_count=valuations_count,
            total_likes=total_likes,
            editable=editable,
        )

    @staticmethod
    def _is_editable(brickset: BrickSet) -> bool:
        """Evaluate RB-01 business rule: can brickset be edited by owner?

        RB-01: BrickSet is editable if:
        - No valuations from other users exist AND
        - Owner's valuation (if exists) has 0 likes

        Note: For performance in list context, this evaluates using prefetched
        or fresh queryset. For paginated lists, this is called post-pagination
        on individual items, so the small performance cost is acceptable.

        Args:
            brickset: BrickSet instance

        Returns:
            bool: True if editable (RB-01 satisfied), False otherwise
        """
        # Check for valuations from other users
        other_users_valuations = brickset.valuations.exclude(
            user_id=brickset.owner_id,
        ).exists()

        if other_users_valuations:
            return False

        # Check owner's valuation for likes (if exists)
        owner_valuation = brickset.valuations.filter(
            user_id=brickset.owner_id,
        ).first()

        if owner_valuation and owner_valuation.likes_count > 0:
            return False

        return True
