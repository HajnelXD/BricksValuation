"""Serializers for owned BrickSet listing endpoint."""
from __future__ import annotations

from rest_framework import serializers


class OwnedBrickSetListItemSerializer(serializers.Serializer):
    """Serialize OwnedBrickSetListItemDTO to JSON for owned bricksets list.

    Represents a single brickset owned by authenticated user with aggregate
    metrics and RB-01 editable flag. All fields are read-only (output only).

    Used in GET /api/v1/users/me/bricksets response.
    """

    id = serializers.IntegerField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    production_status = serializers.CharField(read_only=True)
    completeness = serializers.CharField(read_only=True)
    valuations_count = serializers.IntegerField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    editable = serializers.BooleanField(read_only=True)
