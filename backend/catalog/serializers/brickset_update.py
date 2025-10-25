"""Serializers for BrickSet update (PATCH) endpoint."""
from __future__ import annotations

from rest_framework import serializers

from datastore.domains.catalog_dto import UpdateBrickSetCommand

MAX_INITIAL_ESTIMATE = 999_999


class UpdateBrickSetSerializer(serializers.Serializer):
    """Validate BrickSet partial update payload before handing off to service layer.

    All fields are optional (PATCH semantics), but at least one field must be
    provided in the request. Validation ensures field types and ranges are correct.
    """

    has_box = serializers.BooleanField(required=False)
    owner_initial_estimate = serializers.IntegerField(
        min_value=1,
        max_value=MAX_INITIAL_ESTIMATE,
        required=False,
        allow_null=True,
    )

    def validate(self, data: dict) -> dict:
        """Ensure at least one field is provided (not empty PATCH).

        Args:
            data: Deserialized field data

        Returns:
            data: Validated data

        Raises:
            ValidationError: If no fields provided
        """
        if not data:
            msg = "At least one field must be provided for update."
            raise serializers.ValidationError(msg)
        return data

    def to_command(self) -> UpdateBrickSetCommand:
        """Return validated data mapped to command object.

        Returns:
            UpdateBrickSetCommand with only provided fields (others default to None)

        Raises:
            AssertionError: If serializer not validated before calling
        """
        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_command()."
            raise AssertionError(msg)

        return UpdateBrickSetCommand(**self.validated_data)
