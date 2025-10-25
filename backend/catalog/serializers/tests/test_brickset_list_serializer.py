"""Tests for BrickSet list serializers."""
from __future__ import annotations

from django.test import TestCase
from pytest import raises as pytest_raises

from catalog.serializers.brickset_list import (
    BrickSetFilterSerializer,
    TopValuationSummarySerializer,
    BrickSetListItemSerializer,
)
from catalog.models import ProductionStatus, Completeness
from datastore.domains.catalog_dto import (
    TopValuationSummaryDTO,
    BrickSetListItemDTO,
)


class BrickSetFilterSerializerTests(TestCase):
    """Test suite for BrickSetFilterSerializer."""

    def test_valid_data_all_fields(self) -> None:
        """Test serializer accepts all valid fields."""
        data = {
            "page": 2,
            "page_size": 50,
            "q": "12345",
            "production_status": ProductionStatus.ACTIVE,
            "completeness": Completeness.COMPLETE,
            "has_instructions": True,
            "has_box": False,
            "is_factory_sealed": True,
            "ordering": "-created_at",
        }
        serializer = BrickSetFilterSerializer(data=data)
        assert serializer.is_valid()

    def test_valid_data_no_fields(self) -> None:
        """Test serializer accepts empty data (all optional)."""
        serializer = BrickSetFilterSerializer(data={})
        assert serializer.is_valid()

    def test_valid_data_partial_fields(self) -> None:
        """Test serializer accepts partial data."""
        data = {
            "page": 1,
            "q": "search",
        }
        serializer = BrickSetFilterSerializer(data=data)
        assert serializer.is_valid()

    def test_page_validation_minimum_value(self) -> None:
        """Test that page must be >= 1."""
        serializer = BrickSetFilterSerializer(data={"page": 0})
        assert not serializer.is_valid()
        assert "page" in serializer.errors

    def test_page_validation_negative_value(self) -> None:
        """Test that page cannot be negative."""
        serializer = BrickSetFilterSerializer(data={"page": -1})
        assert not serializer.is_valid()
        assert "page" in serializer.errors

    def test_page_size_validation_minimum_value(self) -> None:
        """Test that page_size must be >= 1."""
        serializer = BrickSetFilterSerializer(data={"page_size": 0})
        assert not serializer.is_valid()
        assert "page_size" in serializer.errors

    def test_page_size_validation_maximum_value(self) -> None:
        """Test that page_size must be <= 100."""
        serializer = BrickSetFilterSerializer(data={"page_size": 101})
        assert not serializer.is_valid()
        assert "page_size" in serializer.errors

    def test_page_size_validation_max_boundary(self) -> None:
        """Test that page_size accepts exactly 100."""
        serializer = BrickSetFilterSerializer(data={"page_size": 100})
        assert serializer.is_valid()

    def test_production_status_validation_invalid_choice(self) -> None:
        """Test that invalid production_status is rejected."""
        serializer = BrickSetFilterSerializer(
            data={"production_status": "INVALID"}
        )
        assert not serializer.is_valid()
        assert "production_status" in serializer.errors

    def test_production_status_validation_active(self) -> None:
        """Test that ACTIVE production_status is accepted."""
        serializer = BrickSetFilterSerializer(
            data={"production_status": ProductionStatus.ACTIVE}
        )
        assert serializer.is_valid()

    def test_production_status_validation_retired(self) -> None:
        """Test that RETIRED production_status is accepted."""
        serializer = BrickSetFilterSerializer(
            data={"production_status": ProductionStatus.RETIRED}
        )
        assert serializer.is_valid()

    def test_completeness_validation_invalid_choice(self) -> None:
        """Test that invalid completeness is rejected."""
        serializer = BrickSetFilterSerializer(
            data={"completeness": "INVALID"}
        )
        assert not serializer.is_valid()
        assert "completeness" in serializer.errors

    def test_completeness_validation_complete(self) -> None:
        """Test that COMPLETE completeness is accepted."""
        serializer = BrickSetFilterSerializer(
            data={"completeness": Completeness.COMPLETE}
        )
        assert serializer.is_valid()

    def test_completeness_validation_incomplete(self) -> None:
        """Test that INCOMPLETE completeness is accepted."""
        serializer = BrickSetFilterSerializer(
            data={"completeness": Completeness.INCOMPLETE}
        )
        assert serializer.is_valid()

    def test_ordering_validation_invalid_choice(self) -> None:
        """Test that invalid ordering is rejected."""
        serializer = BrickSetFilterSerializer(
            data={"ordering": "-invalid_field"}
        )
        assert not serializer.is_valid()
        assert "ordering" in serializer.errors

    def test_ordering_validation_all_valid_choices(self) -> None:
        """Test that all valid orderings are accepted."""
        valid_orderings = [
            "created_at",
            "-created_at",
            "valuations_count",
            "-valuations_count",
            "total_likes",
            "-total_likes",
        ]
        for ordering in valid_orderings:
            serializer = BrickSetFilterSerializer(data={"ordering": ordering})
            assert serializer.is_valid(), f"Ordering '{ordering}' should be valid"

    def test_has_instructions_validation_true(self) -> None:
        """Test that has_instructions=true is accepted."""
        serializer = BrickSetFilterSerializer(data={"has_instructions": True})
        assert serializer.is_valid()

    def test_has_instructions_validation_false(self) -> None:
        """Test that has_instructions=false is accepted."""
        serializer = BrickSetFilterSerializer(data={"has_instructions": False})
        assert serializer.is_valid()

    def test_has_box_validation_true(self) -> None:
        """Test that has_box=true is accepted."""
        serializer = BrickSetFilterSerializer(data={"has_box": True})
        assert serializer.is_valid()

    def test_has_box_validation_false(self) -> None:
        """Test that has_box=false is accepted."""
        serializer = BrickSetFilterSerializer(data={"has_box": False})
        assert serializer.is_valid()

    def test_is_factory_sealed_validation_true(self) -> None:
        """Test that is_factory_sealed=true is accepted."""
        serializer = BrickSetFilterSerializer(data={"is_factory_sealed": True})
        assert serializer.is_valid()

    def test_is_factory_sealed_validation_false(self) -> None:
        """Test that is_factory_sealed=false is accepted."""
        serializer = BrickSetFilterSerializer(data={"is_factory_sealed": False})
        assert serializer.is_valid()

    def test_all_fields_are_optional(self) -> None:
        """Test that all fields are optional."""
        serializer = BrickSetFilterSerializer(data={})
        assert serializer.is_valid()

    def test_q_allows_empty_string(self) -> None:
        """Test that q field allows empty string."""
        serializer = BrickSetFilterSerializer(data={"q": ""})
        assert serializer.is_valid()

    def test_q_allows_search_string(self) -> None:
        """Test that q field accepts search string."""
        serializer = BrickSetFilterSerializer(data={"q": "12345"})
        assert serializer.is_valid()

    def test_to_filter_dict_returns_validated_data(self) -> None:
        """Test that to_filter_dict returns validated data."""
        data = {
            "page": 2,
            "page_size": 50,
            "q": "search",
        }
        serializer = BrickSetFilterSerializer(data=data)
        assert serializer.is_valid()
        filters = serializer.to_filter_dict()
        assert filters["page"] == 2
        assert filters["page_size"] == 50
        assert filters["q"] == "search"

    def test_to_filter_dict_raises_on_unvalidated(self) -> None:
        """Test that to_filter_dict raises AssertionError if not validated."""
        serializer = BrickSetFilterSerializer(data={})
        with pytest_raises(AssertionError):  # noqa: WPS229
            serializer.to_filter_dict()


class TopValuationSummarySerializerTests(TestCase):
    """Test suite for TopValuationSummarySerializer."""

    def test_serialize_top_valuation_dto_to_dict(self) -> None:
        """Test serializing TopValuationSummaryDTO to dict."""
        dto = TopValuationSummaryDTO(
            id=77,
            value=400,
            currency="PLN",
            likes_count=9,
            user_id=99,
        )
        serializer = TopValuationSummarySerializer(dto)
        data = serializer.data

        assert data["id"] == 77
        assert data["value"] == 400
        assert data["currency"] == "PLN"
        assert data["likes_count"] == 9
        assert data["user_id"] == 99

    def test_all_fields_are_read_only(self) -> None:
        """Test that all fields are read-only."""
        serializer = TopValuationSummarySerializer()
        for field in serializer.fields.values():
            assert field.read_only

    def test_serialized_data_contains_all_fields(self) -> None:
        """Test that serialized data has all required fields."""
        dto = TopValuationSummaryDTO(
            id=1,
            value=100,
            currency="PLN",
            likes_count=5,
            user_id=10,
        )
        serializer = TopValuationSummarySerializer(dto)
        data = serializer.data

        assert "id" in data
        assert "value" in data
        assert "currency" in data
        assert "likes_count" in data
        assert "user_id" in data


class BrickSetListItemSerializerTests(TestCase):
    """Test suite for BrickSetListItemSerializer."""

    def test_serialize_brickset_dto_to_dict(self) -> None:
        """Test serializing BrickSetListItemDTO to dict."""
        dto = BrickSetListItemDTO(
            id=10,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_id=42,
            owner_initial_estimate=350,
            valuations_count=5,
            total_likes=12,
            top_valuation=None,
        )
        serializer = BrickSetListItemSerializer(dto)
        data = serializer.data

        assert data["id"] == 10
        assert data["number"] == 12345
        assert data["production_status"] == ProductionStatus.ACTIVE
        assert data["completeness"] == Completeness.COMPLETE
        assert data["has_instructions"] is True
        assert data["has_box"] is False
        assert data["is_factory_sealed"] is False
        assert data["owner_id"] == 42
        assert data["owner_initial_estimate"] == 350
        assert data["valuations_count"] == 5
        assert data["total_likes"] == 12
        assert data["top_valuation"] is None

    def test_serialize_with_null_top_valuation(self) -> None:
        """Test serializing with top_valuation=None."""
        dto = BrickSetListItemDTO(
            id=11,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=True,
            is_factory_sealed=False,
            owner_id=43,
            owner_initial_estimate=None,
            valuations_count=0,
            total_likes=0,
            top_valuation=None,
        )
        serializer = BrickSetListItemSerializer(dto)
        data = serializer.data

        assert data["top_valuation"] is None

    def test_serialize_with_populated_top_valuation(self) -> None:
        """Test serializing with populated top_valuation."""
        top_val = TopValuationSummaryDTO(
            id=77,
            value=400,
            currency="PLN",
            likes_count=9,
            user_id=99,
        )
        dto = BrickSetListItemDTO(
            id=10,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_id=42,
            owner_initial_estimate=350,
            valuations_count=5,
            total_likes=12,
            top_valuation=top_val,
        )
        serializer = BrickSetListItemSerializer(dto)
        data = serializer.data

        assert data["top_valuation"] is not None
        assert data["top_valuation"]["id"] == 77
        assert data["top_valuation"]["value"] == 400
        assert data["top_valuation"]["likes_count"] == 9

    def test_all_fields_are_read_only(self) -> None:
        """Test that all fields are read-only."""
        serializer = BrickSetListItemSerializer()
        for field in serializer.fields.values():
            assert field.read_only

    def test_null_owner_initial_estimate_is_serialized_correctly(self) -> None:
        """Test that null owner_initial_estimate is handled correctly."""
        dto = BrickSetListItemDTO(
            id=1,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_id=1,
            owner_initial_estimate=None,
            valuations_count=0,
            total_likes=0,
            top_valuation=None,
        )
        serializer = BrickSetListItemSerializer(dto)
        data = serializer.data

        assert data["owner_initial_estimate"] is None

    def test_serialized_data_contains_all_fields(self) -> None:
        """Test that serialized data has all required fields."""
        dto = BrickSetListItemDTO(
            id=1,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_id=1,
            owner_initial_estimate=100,
            valuations_count=0,
            total_likes=0,
            top_valuation=None,
        )
        serializer = BrickSetListItemSerializer(dto)
        data = serializer.data

        required_fields = [
            "id",
            "number",
            "production_status",
            "completeness",
            "has_instructions",
            "has_box",
            "is_factory_sealed",
            "owner_id",
            "owner_initial_estimate",
            "valuations_count",
            "total_likes",
            "top_valuation",
        ]
        for field in required_fields:
            assert field in data
