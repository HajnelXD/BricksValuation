"""Serializers for BrickSet creation endpoint."""
from __future__ import annotations

from rest_framework import serializers

from catalog.models import ProductionStatus, Completeness
from datastore.domains.catalog_dto import CreateBrickSetCommand

MAX_SET_NUMBER = 9_999_999
MAX_INITIAL_ESTIMATE = 999_999


class CreateBrickSetSerializer(serializers.Serializer):
    """Validate BrickSet creation payload before handing off to service layer."""

    number = serializers.IntegerField(
        min_value=0,
        max_value=MAX_SET_NUMBER,
    )
    production_status = serializers.ChoiceField(
        choices=[ProductionStatus.ACTIVE, ProductionStatus.RETIRED],
    )
    completeness = serializers.ChoiceField(
        choices=[Completeness.COMPLETE, Completeness.INCOMPLETE],
    )
    has_instructions = serializers.BooleanField()
    has_box = serializers.BooleanField()
    is_factory_sealed = serializers.BooleanField()
    owner_initial_estimate = serializers.IntegerField(
        min_value=1,
        max_value=MAX_INITIAL_ESTIMATE,
        required=False,
        allow_null=True,
        default=None,
    )

    def to_command(self) -> CreateBrickSetCommand:
        """Return validated data mapped to command object."""

        if not hasattr(self, "_validated_data"):
            msg = "Serializer must be validated before calling to_command()."
            raise AssertionError(msg)
        return CreateBrickSetCommand(**self.validated_data)
