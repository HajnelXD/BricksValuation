"""Serializer for Like response output.

Read-only serializer for POST /valuations/{valuation_id}/likes response (201 Created).
Serializes LikeDTO to JSON with valuation_id, user_id, and created_at timestamp.
"""
from __future__ import annotations

from rest_framework import serializers


class LikeSerializer(serializers.Serializer):
    """Serialize LikeDTO to JSON for Like creation response.

    Represents a created Like with all required fields.
    All fields are read-only (output only). Designed for response of
    POST /valuations/{id}/likes endpoint (HTTP 201 Created).
    """

    valuation_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
