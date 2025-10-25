"""Tests for BrickSet detail serializers."""
from __future__ import annotations

from datetime import datetime
from django.test import TestCase

from catalog.serializers.brickset_detail import (
    ValuationInlineSerializer,
    BrickSetDetailSerializer,
)
from datastore.domains.catalog_dto import (
    ValuationInlineDTO,
    BrickSetDetailDTO,
)


class ValuationInlineSerializerTests(TestCase):
    """Test suite for ValuationInlineSerializer."""

    def test_serializes_all_fields(self) -> None:
        """Test serializer converts all DTO fields to JSON."""
        created_at = datetime(2025, 10, 20, 14, 23, 45, 123000)
        valuation_dto = ValuationInlineDTO(
            id=77,
            user_id=99,
            value=400,
            currency="PLN",
            comment="Looks complete",
            likes_count=9,
            created_at=created_at,
        )

        serializer = ValuationInlineSerializer(valuation_dto)
        data = serializer.data

        assert data["id"] == 77
        assert data["user_id"] == 99
        assert data["value"] == 400
        assert data["currency"] == "PLN"
        assert data["comment"] == "Looks complete"
        assert data["likes_count"] == 9
        assert "created_at" in data

    def test_handles_null_comment(self) -> None:
        """Test serializer handles null comment field."""
        created_at = datetime(2025, 10, 21, 9, 15, 22, 456000)
        valuation_dto = ValuationInlineDTO(
            id=78,
            user_id=101,
            value=380,
            currency="PLN",
            comment=None,
            likes_count=3,
            created_at=created_at,
        )

        serializer = ValuationInlineSerializer(valuation_dto)
        data = serializer.data

        assert data["comment"] is None

    def test_formats_datetime_iso8601(self) -> None:
        """Test serializer formats datetime as ISO8601."""
        created_at = datetime(2025, 10, 20, 14, 23, 45, 123000)
        valuation_dto = ValuationInlineDTO(
            id=1,
            user_id=1,
            value=100,
            currency="PLN",
            comment=None,
            likes_count=0,
            created_at=created_at,
        )

        serializer = ValuationInlineSerializer(valuation_dto)
        data = serializer.data

        # DRF should format as ISO string
        assert isinstance(data["created_at"], str)
        assert "2025-10-20" in data["created_at"]

    def test_all_fields_read_only(self) -> None:
        """Test all fields are marked read-only."""
        field_names = [
            "id",
            "user_id",
            "value",
            "currency",
            "comment",
            "likes_count",
            "created_at",
        ]
        for field_name in field_names:
            field = ValuationInlineSerializer().fields[field_name]
            assert field.read_only is True


class BrickSetDetailSerializerTests(TestCase):
    """Test suite for BrickSetDetailSerializer."""

    def test_serializes_all_fields_no_valuations(self) -> None:
        """Test serializer converts BrickSetDetailDTO with no valuations."""
        created_at = datetime(2025, 10, 15, 10, 30, 0)
        updated_at = datetime(2025, 10, 15, 10, 30, 0)

        brickset_dto = BrickSetDetailDTO(
            id=1,
            number=10001,
            production_status="ACTIVE",
            completeness="COMPLETE",
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=250,
            owner_id=15,
            valuations=[],
            valuations_count=0,
            total_likes=0,
            created_at=created_at,
            updated_at=updated_at,
        )

        serializer = BrickSetDetailSerializer(brickset_dto)
        data = serializer.data

        assert data["id"] == 1
        assert data["number"] == 10001
        assert data["production_status"] == "ACTIVE"
        assert data["completeness"] == "COMPLETE"
        assert data["has_instructions"] is True
        assert data["has_box"] is True
        assert data["is_factory_sealed"] is False
        assert data["owner_initial_estimate"] == 250
        assert data["owner_id"] == 15
        assert data["valuations"] == []
        assert data["valuations_count"] == 0
        assert data["total_likes"] == 0

    def test_serializes_with_multiple_valuations(self) -> None:
        """Test serializer with nested valuations list."""
        created_at = datetime(2025, 10, 10, 8, 15, 30)
        updated_at = datetime(2025, 10, 10, 8, 15, 30)

        valuation1 = ValuationInlineDTO(
            id=101,
            user_id=25,
            value=450,
            currency="PLN",
            comment="Excellent",
            likes_count=15,
            created_at=datetime(2025, 10, 20, 14, 23, 45),
        )
        valuation2 = ValuationInlineDTO(
            id=102,
            user_id=30,
            value=420,
            currency="PLN",
            comment=None,
            likes_count=8,
            created_at=datetime(2025, 10, 21, 9, 15, 22),
        )

        brickset_dto = BrickSetDetailDTO(
            id=42,
            number=12345,
            production_status="RETIRED",
            completeness="COMPLETE",
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=None,
            owner_id=99,
            valuations=[valuation1, valuation2],
            valuations_count=2,
            total_likes=23,
            created_at=created_at,
            updated_at=updated_at,
        )

        serializer = BrickSetDetailSerializer(brickset_dto)
        data = serializer.data

        assert data["id"] == 42
        assert len(data["valuations"]) == 2
        assert data["valuations"][0]["id"] == 101
        assert data["valuations"][0]["value"] == 450
        assert data["valuations"][1]["id"] == 102
        assert data["valuations"][1]["comment"] is None
        assert data["valuations_count"] == 2
        assert data["total_likes"] == 23

    def test_handles_null_owner_initial_estimate(self) -> None:
        """Test serializer with null owner_initial_estimate."""
        created_at = datetime(2025, 10, 15, 10, 30, 0)
        updated_at = datetime(2025, 10, 15, 10, 30, 0)

        brickset_dto = BrickSetDetailDTO(
            id=5,
            number=99999,
            production_status="ACTIVE",
            completeness="INCOMPLETE",
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=None,
            owner_id=42,
            valuations=[],
            valuations_count=0,
            total_likes=0,
            created_at=created_at,
            updated_at=updated_at,
        )

        serializer = BrickSetDetailSerializer(brickset_dto)
        data = serializer.data

        assert data["owner_initial_estimate"] is None

    def test_all_fields_read_only(self) -> None:
        """Test all fields are marked read-only."""
        field_names = [
            "id",
            "number",
            "production_status",
            "completeness",
            "has_instructions",
            "has_box",
            "is_factory_sealed",
            "owner_initial_estimate",
            "owner_id",
            "valuations",
            "valuations_count",
            "total_likes",
            "created_at",
            "updated_at",
        ]
        for field_name in field_names:
            field = BrickSetDetailSerializer().fields[field_name]
            assert field.read_only is True

    def test_nested_serializer_structure(self) -> None:
        """Test nested ValuationInlineSerializer is properly configured."""
        serializer = BrickSetDetailSerializer()
        valuations_field = serializer.fields["valuations"]

        # Should be many=True
        assert valuations_field.many is True
        # Child should be ValuationInlineSerializer
        assert isinstance(valuations_field.child, ValuationInlineSerializer)
