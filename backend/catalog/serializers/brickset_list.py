"""Serializers for BrickSet listing endpoint."""
from __future__ import annotations

from rest_framework import serializers

from catalog.models import ProductionStatus, Completeness
from datastore.domains.catalog_dto import TopValuationSummaryDTO  # noqa: F401


class BrickSetFilterSerializer(serializers.Serializer):
    """Validate query parameters for GET /api/v1/bricksets endpoint.

    Validates pagination, search, filtering and ordering parameters.
    All fields are optional with sensible defaults.
    """

    ORDERING_CHOICES = [
        "number",
        "-number",
        "created_at",
        "-created_at",
        "valuations_count",
        "-valuations_count",
        "total_likes",
        "-total_likes",
    ]

    page = serializers.IntegerField(
        min_value=1,
        required=False,
        help_text="Page number (default 1).",
    )
    page_size = serializers.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        help_text="Items per page (default 20, max 100).",
    )
    q = serializers.CharField(  # noqa: WPS111
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        help_text="Search by set number (partial match).",
    )
    production_status = serializers.ChoiceField(
        choices=[ProductionStatus.ACTIVE, ProductionStatus.RETIRED],
        required=False,
        help_text="Filter by production status.",
    )
    completeness = serializers.ChoiceField(
        choices=[Completeness.COMPLETE, Completeness.INCOMPLETE],
        required=False,
        help_text="Filter by completeness.",
    )
    has_instructions = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Filter by instructions.",
    )
    has_box = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Filter by box presence.",
    )
    is_factory_sealed = serializers.BooleanField(
        required=False,
        allow_null=True,
        help_text="Filter by seal state.",
    )
    ordering = serializers.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        help_text="Sort order.",
    )

    def to_filter_dict(self) -> dict:
        """Convert validated data to filter dictionary for service layer.

        Returns only fields that were explicitly provided (removes None values).
        This prevents applying default None values to optional filters.
        """
        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_filter_dict()."
            raise AssertionError(msg)

        return {key: value for key, value in self.validated_data.items() if value is not None}


class TopValuationSummarySerializer(serializers.Serializer):
    """Serialize TopValuationSummaryDTO to JSON.

    Represents the most-liked valuation for a brickset in list responses.
    """

    id = serializers.IntegerField(read_only=True)
    value = serializers.IntegerField(read_only=True)  # noqa: WPS110
    currency = serializers.CharField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)


class BrickSetListItemSerializer(serializers.Serializer):
    """Serialize BrickSetListItemDTO to JSON for list responses.

    Represents a single brickset with aggregate metrics and top valuation summary.
    All fields are read-only (output only).
    """

    id = serializers.IntegerField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    production_status = serializers.CharField(read_only=True)
    completeness = serializers.CharField(read_only=True)
    has_instructions = serializers.BooleanField(read_only=True)
    has_box = serializers.BooleanField(read_only=True)
    is_factory_sealed = serializers.BooleanField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)
    owner_initial_estimate = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )
    valuations_count = serializers.IntegerField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    top_valuation = TopValuationSummarySerializer(
        read_only=True,
        allow_null=True,
    )
