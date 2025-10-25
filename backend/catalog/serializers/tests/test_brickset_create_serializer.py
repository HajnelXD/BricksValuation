"""Tests for CreateBrickSetSerializer."""
from __future__ import annotations

from django.test import TestCase

from catalog.serializers.brickset_create import CreateBrickSetSerializer
from datastore.domains.catalog_dto import CreateBrickSetCommand


class CreateBrickSetSerializerTests(TestCase):
    """Test CreateBrickSetSerializer validation and to_command() conversion."""

    def test_valid_data_with_all_fields(self) -> None:
        """Serializer accepts valid payload with all fields."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 360,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["number"] == 12345
        assert serializer.validated_data["owner_initial_estimate"] == 360

    def test_valid_data_without_owner_initial_estimate(self) -> None:
        """Serializer accepts valid payload without optional estimate."""
        payload = {
            "number": 67890,
            "production_status": "RETIRED",
            "completeness": "INCOMPLETE",
            "has_instructions": False,
            "has_box": False,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["owner_initial_estimate"] is None

    def test_number_at_minimum_value(self) -> None:
        """Serializer accepts number=0 (minimum)."""
        payload = {
            "number": 0,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_number_at_maximum_value(self) -> None:
        """Serializer accepts number=9,999,999 (maximum)."""
        payload = {
            "number": 9999999,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_invalid_number_exceeds_maximum(self) -> None:
        """Serializer rejects number > 9,999,999."""
        payload = {
            "number": 10000000,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "number" in serializer.errors

    def test_invalid_number_negative(self) -> None:
        """Serializer rejects negative number."""
        payload = {
            "number": -1,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "number" in serializer.errors

    def test_invalid_production_status_not_in_choices(self) -> None:
        """Serializer rejects invalid production_status."""
        payload = {
            "number": 12345,
            "production_status": "INVALID",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "production_status" in serializer.errors

    def test_invalid_completeness_not_in_choices(self) -> None:
        """Serializer rejects invalid completeness."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "UNKNOWN",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "completeness" in serializer.errors

    def test_owner_initial_estimate_at_minimum_value(self) -> None:
        """Serializer accepts owner_initial_estimate=1 (minimum)."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 1,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_owner_initial_estimate_at_maximum_value(self) -> None:
        """Serializer accepts owner_initial_estimate=999,999 (maximum)."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 999999,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_invalid_owner_initial_estimate_zero(self) -> None:
        """Serializer rejects owner_initial_estimate=0."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 0,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "owner_initial_estimate" in serializer.errors

    def test_invalid_owner_initial_estimate_exceeds_maximum(self) -> None:
        """Serializer rejects owner_initial_estimate > 999,999."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 1000000,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "owner_initial_estimate" in serializer.errors

    def test_missing_required_field_number(self) -> None:
        """Serializer rejects missing number."""
        payload = {
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "number" in serializer.errors

    def test_missing_required_field_production_status(self) -> None:
        """Serializer rejects missing production_status."""
        payload = {
            "number": 12345,
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "production_status" in serializer.errors

    def test_missing_required_field_completeness(self) -> None:
        """Serializer rejects missing completeness."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        assert not serializer.is_valid()
        assert "completeness" in serializer.errors

    def test_to_command_creates_correct_command_object(self) -> None:
        """to_command() returns CreateBrickSetCommand with validated data."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 360,
        }
        serializer = CreateBrickSetSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command()

        assert isinstance(command, CreateBrickSetCommand)
        assert command.number == 12345
        assert command.production_status == "ACTIVE"
        assert command.owner_initial_estimate == 360

    def test_to_command_includes_all_validated_fields(self) -> None:
        """to_command() includes all fields from validated_data."""
        payload = {
            "number": 67890,
            "production_status": "RETIRED",
            "completeness": "INCOMPLETE",
            "has_instructions": False,
            "has_box": False,
            "is_factory_sealed": True,
        }
        serializer = CreateBrickSetSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command()

        assert command.has_instructions is False
        assert command.has_box is False
        assert command.is_factory_sealed is True
        assert command.owner_initial_estimate is None

    def test_to_command_raises_assertion_error_without_validation(self) -> None:
        """to_command() raises AssertionError if not validated."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }
        serializer = CreateBrickSetSerializer(data=payload)

        with self.assertRaises(AssertionError):
            serializer.to_command()
