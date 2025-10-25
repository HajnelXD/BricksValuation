"""Serializers for valuation list endpoint."""
from __future__ import annotations

from rest_framework import serializers


class ValuationListItemSerializer(serializers.Serializer):
    """Read-only serializer for ValuationListItemDTO.

    Validates output structure for GET /bricksets/{brickset_id}/valuations
    endpoint. All fields are read-only as this is a response-only serializer.
    """

    id = serializers.IntegerField(
        read_only=True,
        help_text="Valuation unique identifier.",
    )
    user_id = serializers.IntegerField(
        read_only=True,
        help_text="ID of the user who created the valuation.",
    )
    value = serializers.IntegerField(
        read_only=True,
        help_text="Valuation value (1-999,999).",
    )
    currency = serializers.CharField(
        read_only=True,
        help_text="Currency code (e.g., 'PLN').",
    )
    comment = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="Optional comment about the valuation.",
    )
    likes_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of likes this valuation received.",
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the valuation was created.",
    )
