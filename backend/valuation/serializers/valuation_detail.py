"""Serializers for valuation detail responses."""
from __future__ import annotations

from rest_framework import serializers


class ValuationSerializer(serializers.Serializer):
    """Serialize ValuationDTO to JSON for valuation responses.

    Represents a single user's valuation of a BrickSet with all metadata.
    All fields are read-only (output only).
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
    updated_at = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )
