"""Serializers for valuation creation endpoint."""
from __future__ import annotations

from rest_framework import serializers

from datastore.domains.valuation_dto import CreateValuationCommand

MAX_VALUATION = 999_999
MAX_CURRENCY_LENGTH = 3


class CreateValuationSerializer(serializers.Serializer):
    """Validate Valuation creation payload before handing off to service layer.

    All fields are validated for format and range. The to_command() method
    converts validated data to CreateValuationCommand with brickset_id from
    the URL path parameter.
    """

    value = serializers.IntegerField(
        min_value=1,
        max_value=MAX_VALUATION,
        help_text="Valuation value (1-999,999).",
    )
    currency = serializers.CharField(
        max_length=MAX_CURRENCY_LENGTH,
        required=False,
        allow_blank=False,
        default="PLN",
        help_text="Currency code (max 3 characters, default 'PLN').",
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
        help_text="Optional comment about the valuation.",
    )

    def to_command(self, brickset_id: int) -> CreateValuationCommand:
        """Convert validated data to CreateValuationCommand.

        Args:
            brickset_id: BrickSet identifier from URL path parameter.

        Returns:
            CreateValuationCommand with brickset_id and validated fields.

        Raises:
            AssertionError: If serializer was not validated before calling.
        """
        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_command()."
            raise AssertionError(msg)

        return CreateValuationCommand(
            brickset_id=brickset_id,
            **self.validated_data,
        )
