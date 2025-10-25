"""Service implementing BrickSet listing with filters, aggregations and sorting."""
from __future__ import annotations

from django.db.models import (
    Count,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from catalog.models import BrickSet
from datastore.domains.catalog_dto import (
    TopValuationSummaryDTO,
    BrickSetListItemDTO,
)
from valuation.models import Valuation


class BrickSetListService:  # noqa: WPS338
    """Coordinate BrickSet listing with filters, aggregations and sorting."""

    ALLOWED_ORDERINGS = [
        "created_at",
        "-created_at",
        "valuations_count",
        "-valuations_count",
        "total_likes",
        "-total_likes",
    ]

    DEFAULT_ORDERING = "-created_at"

    def get_queryset(self, filters: dict) -> QuerySet:
        """Build and return optimized QuerySet with filters and annotations.

        Flow:
        1. Start with base QuerySet
        2. Apply text search filter (q parameter)
        3. Apply boolean and choice filters
        4. Add count annotations (valuations_count, total_likes)
        5. Add subquery for top valuation
        6. Apply ordering
        """
        queryset = BrickSet.bricksets.all()

        # Apply filters
        queryset = self._apply_search_filter(queryset, filters.get("q"))
        queryset = self._apply_status_filters(queryset, filters)

        # Add aggregations and annotations
        queryset = self._add_aggregations(queryset)

        # Apply ordering
        ordering = filters.get("ordering", self.DEFAULT_ORDERING)
        queryset = self._apply_ordering(queryset, ordering)

        return queryset

    def _apply_search_filter(self, queryset: QuerySet, query: str | None) -> QuerySet:
        """Filter bricksets by partial match on set number."""
        if query:
            queryset = queryset.filter(number__icontains=query)
        return queryset

    def _apply_status_filters(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """Apply production_status, completeness and boolean condition filters."""
        production_status = filters.get("production_status")
        if production_status:
            queryset = queryset.filter(production_status=production_status)

        completeness = filters.get("completeness")
        if completeness:
            queryset = queryset.filter(completeness=completeness)

        if filters.get("has_instructions") is not None:
            queryset = queryset.filter(has_instructions=filters["has_instructions"])

        if filters.get("has_box") is not None:
            queryset = queryset.filter(has_box=filters["has_box"])

        if filters.get("is_factory_sealed") is not None:
            queryset = queryset.filter(is_factory_sealed=filters["is_factory_sealed"])

        return queryset

    def _add_aggregations(self, queryset: QuerySet) -> QuerySet:
        """Add annotations for valuations_count, total_likes and top_valuation.

        Optimizations:
        - valuations_count: Count('valuations')
        - total_likes: Coalesce(Sum('valuations__likes_count'), 0) to handle no valuations
        - top_valuation_id: Subquery selecting valuation with max likes_count
        """
        top_valuation_subquery = self._get_top_valuation_subquery()

        queryset = queryset.annotate(
            valuations_count=Count("valuations", distinct=True),
            total_likes=Coalesce(
                Sum("valuations__likes_count", output_field=IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            top_valuation_id=Subquery(top_valuation_subquery),
        )

        return queryset

    @staticmethod
    def _get_top_valuation_subquery() -> Subquery:
        """Build subquery to fetch ID of valuation with max likes for each brickset.

        Returns the ID of the valuation with the highest likes_count for each
        brickset. If no valuations exist, returns None.
        """
        top_valuation = (
            Valuation.valuations.filter(brickset=OuterRef("pk"))
            .order_by("-likes_count", "-created_at")
            .values("id")[:1]
        )
        return Subquery(top_valuation, output_field=IntegerField())

    def _apply_ordering(self, queryset: QuerySet, ordering: str) -> QuerySet:
        """Apply ordering by the specified field."""
        if ordering in self.ALLOWED_ORDERINGS:
            queryset = queryset.order_by(ordering)
        return queryset

    def map_to_dto(self, brickset: BrickSet) -> BrickSetListItemDTO:
        """Map a BrickSet instance to BrickSetListItemDTO.

        Expects the queryset to have been annotated with valuations_count,
        total_likes, and top_valuation_id. If top_valuation_id exists,
        fetches the related Valuation to build TopValuationSummaryDTO.
        """
        top_valuation_dto = None

        # Check if top_valuation_id was annotated and exists
        if hasattr(brickset, "top_valuation_id") and brickset.top_valuation_id:
            top_val = Valuation.valuations.filter(
                id=brickset.top_valuation_id
            ).first()
            if top_val:
                top_valuation_dto = TopValuationSummaryDTO(
                    id=top_val.id,
                    value=top_val.value,
                    currency=top_val.currency,
                    likes_count=top_val.likes_count,
                    user_id=top_val.user_id,
                )

        valuations_count = (
            getattr(brickset, "valuations_count", 0) or 0
        )
        total_likes = (
            getattr(brickset, "total_likes", 0) or 0
        )

        return BrickSetListItemDTO(
            id=brickset.id,
            number=brickset.number,
            production_status=brickset.production_status,
            completeness=brickset.completeness,
            has_instructions=brickset.has_instructions,
            has_box=brickset.has_box,
            is_factory_sealed=brickset.is_factory_sealed,
            owner_id=brickset.owner_id,
            owner_initial_estimate=brickset.owner_initial_estimate,
            valuations_count=valuations_count,
            total_likes=total_likes,
            top_valuation=top_valuation_dto,
        )
