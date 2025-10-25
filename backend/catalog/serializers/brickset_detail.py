"""Serializers for BrickSet detail endpoint."""
from __future__ import annotations

from rest_framework import serializers


class ValuationInlineSerializer(serializers.Serializer):
    """Serialize ValuationInlineDTO to JSON for nested valuation objects.

    Represents a single valuation with user, value, currency and metadata.
    All fields are read-only (output only).
    """

    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    value = serializers.IntegerField(read_only=True)  # noqa: WPS110
    currency = serializers.CharField(read_only=True)
    comment = serializers.CharField(
        read_only=True,
        allow_null=True,
    )
    likes_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class BrickSetDetailSerializer(serializers.Serializer):
    """Serialize BrickSetDetailDTO to JSON for detail responses.

    Represents a full brickset with all valuations and aggregate metrics.
    All fields are read-only (output only).
    """

    id = serializers.IntegerField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    production_status = serializers.CharField(read_only=True)
    completeness = serializers.CharField(read_only=True)
    has_instructions = serializers.BooleanField(read_only=True)
    has_box = serializers.BooleanField(read_only=True)
    is_factory_sealed = serializers.BooleanField(read_only=True)
    owner_initial_estimate = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )
    owner_id = serializers.IntegerField(read_only=True)
    valuations = ValuationInlineSerializer(
        read_only=True,
        many=True,
    )
    valuations_count = serializers.IntegerField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
