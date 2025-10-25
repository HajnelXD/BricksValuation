"""Serializers for owned valuation list endpoint."""
from __future__ import annotations

from rest_framework import serializers


class OwnedValuationListItemSerializer(serializers.Serializer):
    """Read-only serializer for OwnedValuationListItemDTO.

    Represents a single valuation owned by authenticated user with nested
    brickset reference. Used in GET /api/v1/users/me/valuations response.
    All fields are read-only (output only).
    """

    id = serializers.IntegerField(
        read_only=True,
        help_text="Valuation unique identifier.",
    )
    brickset = serializers.DictField(
        read_only=True,
        help_text="Nested brickset reference with id and number.",
    )
    value = serializers.IntegerField(
        read_only=True,
        help_text="Valuation value (1-999,999).",
    )
    currency = serializers.CharField(
        read_only=True,
        help_text="Currency code (e.g., 'PLN').",
    )
    likes_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of likes this valuation received.",
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the valuation was created.",
    )
