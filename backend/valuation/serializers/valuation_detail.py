"""Serializers for Valuation detail endpoint."""
from __future__ import annotations

from rest_framework import serializers


class ValuationSerializer(serializers.Serializer):
    """Serialize ValuationDetailDTO to JSON for detail responses.

    Represents a full valuation with all fields including timestamps.
    All fields are read-only (output only). Designed for GET /valuations/{id}
    detail endpoint.
    """

    id = serializers.IntegerField(read_only=True)
    brickset_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    value = serializers.IntegerField(read_only=True)  # noqa: WPS110
    currency = serializers.CharField(read_only=True)
    comment = serializers.CharField(
        read_only=True,
        allow_null=True,
    )
    likes_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# Alias for semantic clarity in detail endpoint context
ValuationDetailSerializer = ValuationSerializer
