"""Tests for CreateValuationSerializer."""
from __future__ import annotations

from django.test import TestCase

from datastore.domains.valuation_dto import CreateValuationCommand
from valuation.serializers.valuation_create import CreateValuationSerializer


class CreateValuationSerializerTests(TestCase):
    """Test CreateValuationSerializer validation and to_command() conversion."""

    def test_valid_data_with_all_fields(self) -> None:
        """Serializer accepts valid payload with all fields."""
        payload = {
            "value": 450,
            "currency": "PLN",
            "comment": "Looks complete and in great condition",
        }
        serializer = CreateValuationSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["value"] == 450
        assert serializer.validated_data["currency"] == "PLN"
        assert serializer.validated_data["comment"] == "Looks complete and in great condition"

    def test_valid_data_without_optional_fields(self) -> None:
        """Serializer accepts valid payload without optional currency and comment."""
        payload = {
            "value": 250,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["value"] == 250
        assert serializer.validated_data["currency"] == "PLN"  # default
        assert serializer.validated_data["comment"] is None

    def test_valid_data_with_only_value_and_comment(self) -> None:
        """Serializer accepts value with comment, omits currency (uses default)."""
        payload = {
            "value": 500,
            "comment": "Used but complete",
        }
        serializer = CreateValuationSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["value"] == 500
        assert serializer.validated_data["currency"] == "PLN"
        assert serializer.validated_data["comment"] == "Used but complete"

    def test_value_at_minimum_value(self) -> None:
        """Serializer accepts value=1 (minimum)."""
        payload = {
            "value": 1,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_value_at_maximum_value(self) -> None:
        """Serializer accepts value=999,999 (maximum)."""
        payload = {
            "value": 999999,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert serializer.is_valid(), serializer.errors

    def test_invalid_value_zero(self) -> None:
        """Serializer rejects value=0 (below minimum)."""
        payload = {
            "value": 0,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_invalid_value_negative(self) -> None:
        """Serializer rejects negative value."""
        payload = {
            "value": -100,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_invalid_value_exceeds_maximum(self) -> None:
        """Serializer rejects value > 999,999."""
        payload = {
            "value": 1000000,
        }
        serializer = CreateValuationSerializer(data=payload)

        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_invalid_currency_exceeds_max_length(self) -> None:
        """Serializer rejects currency longer than 3 characters."""
        payload = {
            "value": 300,
            "currency": "PLNX",
        }
        serializer = CreateValuationSerializer(data=payload)

        assert not serializer.is_valid()
        assert "currency" in serializer.errors

    def test_valid_currency_various_codes(self) -> None:
        """Serializer accepts various valid currency codes."""
        valid_currencies = ("PLN", "EUR", "USD", "GBP", "JPY")
        for currency_code in valid_currencies:
            payload = {
                "value": 300,
                "currency": currency_code,
            }
            serializer = CreateValuationSerializer(data=payload)

            assert serializer.is_valid(), f"Failed for currency {currency_code}: {serializer.errors}"
            assert serializer.validated_data["currency"] == currency_code

    def test_missing_required_field_value(self) -> None:
        """Serializer rejects missing value."""
        payload = {
            "currency": "PLN",
        }
        serializer = CreateValuationSerializer(data=payload)

        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_to_command_returns_command_object(self) -> None:
        """to_command() converts validated data to CreateValuationCommand."""
        payload = {
            "value": 450,
            "currency": "PLN",
            "comment": "Good condition",
        }
        serializer = CreateValuationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command(brickset_id=42)

        assert isinstance(command, CreateValuationCommand)
        assert command.brickset_id == 42
        assert command.value == 450
        assert command.currency == "PLN"
        assert command.comment == "Good condition"

    def test_to_command_includes_brickset_id_from_path(self) -> None:
        """to_command() includes brickset_id from function parameter."""
        payload = {
            "value": 300,
        }
        serializer = CreateValuationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command(brickset_id=999)

        assert command.brickset_id == 999

    def test_to_command_with_default_currency(self) -> None:
        """to_command() uses default currency when not provided."""
        payload = {
            "value": 200,
            "comment": "Sealed",
        }
        serializer = CreateValuationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        command = serializer.to_command(brickset_id=10)

        assert command.currency == "PLN"

    def test_to_command_raises_assertion_error_without_validation(self) -> None:
        """to_command() raises AssertionError if not validated."""
        payload = {
            "value": 450,
        }
        serializer = CreateValuationSerializer(data=payload)

        with self.assertRaises(AssertionError):
            serializer.to_command(brickset_id=42)
