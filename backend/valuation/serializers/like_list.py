"""Serializers for like list endpoint."""
from __future__ import annotations

from rest_framework import serializers


class LikeListItemSerializer(serializers.Serializer):
    """Read-only serializer for LikeListItemDTO.

    Validates output structure for GET /valuations/{valuation_id}/likes
    endpoint. All fields are read-only as this is a response-only serializer.
    Represents minimal user reference data (only ID, not username/email for
    privacy) and creation timestamp for a like on a valuation.
    """

    user_id = serializers.IntegerField(
        read_only=True,
        help_text="ID of the user who liked the valuation.",
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the like was created.",
    )
