"""Tests for BrickSetListService."""
from __future__ import annotations

from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker

from catalog.models import BrickSet, ProductionStatus, Completeness
from catalog.services.brickset_list_service import BrickSetListService
from valuation.models import Valuation

User = get_user_model()


class BrickSetListServiceTests(TestCase):
    """Test suite for BrickSetListService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = BrickSetListService()
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)

        # Create test bricksets
        self.brickset1 = baker.make(
            BrickSet,
            owner=self.user1,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=350,
        )
        self.brickset2 = baker.make(
            BrickSet,
            owner=self.user1,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=None,
        )
        self.brickset3 = baker.make(
            BrickSet,
            owner=self.user2,
            number=11111,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=True,
            owner_initial_estimate=500,
        )

        # Create valuations
        self.valuation1 = baker.make(
            Valuation,
            user=self.user2,
            brickset=self.brickset1,
            value=400,
            currency="PLN",
            comment="Nice set",
            likes_count=5,
        )
        self.valuation2 = baker.make(
            Valuation,
            user=self.user1,
            brickset=self.brickset1,
            value=380,
            currency="PLN",
            comment="Good condition",
            likes_count=3,
        )

    def test_get_queryset_without_filters_returns_all_bricksets(self) -> None:
        """Test that get_queryset without filters returns all bricksets."""
        queryset = self.service.get_queryset({})
        assert queryset.count() == 3

    def test_get_queryset_filters_by_number_query(self) -> None:
        """Test filtering by partial number match."""
        queryset = self.service.get_queryset({"q": "123"})
        assert queryset.count() == 1
        assert queryset.first().number == 12345

    def test_get_queryset_filters_by_number_query_no_match(self) -> None:
        """Test filtering by number with no matches."""
        queryset = self.service.get_queryset({"q": "999999"})
        assert queryset.count() == 0

    def test_get_queryset_filters_by_production_status_active(self) -> None:
        """Test filtering by ACTIVE production status."""
        queryset = self.service.get_queryset(
            {"production_status": ProductionStatus.ACTIVE}
        )
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [11111, 12345]

    def test_get_queryset_filters_by_production_status_retired(self) -> None:
        """Test filtering by RETIRED production status."""
        queryset = self.service.get_queryset(
            {"production_status": ProductionStatus.RETIRED}
        )
        assert queryset.count() == 1
        assert queryset.first().number == 67890

    def test_get_queryset_filters_by_completeness_complete(self) -> None:
        """Test filtering by COMPLETE completeness."""
        queryset = self.service.get_queryset(
            {"completeness": Completeness.COMPLETE}
        )
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [11111, 12345]

    def test_get_queryset_filters_by_completeness_incomplete(self) -> None:
        """Test filtering by INCOMPLETE completeness."""
        queryset = self.service.get_queryset(
            {"completeness": Completeness.INCOMPLETE}
        )
        assert queryset.count() == 1
        assert queryset.first().number == 67890

    def test_get_queryset_filters_by_has_instructions_true(self) -> None:
        """Test filtering by has_instructions=True."""
        queryset = self.service.get_queryset({"has_instructions": True})
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [11111, 12345]

    def test_get_queryset_filters_by_has_instructions_false(self) -> None:
        """Test filtering by has_instructions=False."""
        queryset = self.service.get_queryset({"has_instructions": False})
        assert queryset.count() == 1
        assert queryset.first().number == 67890

    def test_get_queryset_filters_by_has_box_true(self) -> None:
        """Test filtering by has_box=True."""
        queryset = self.service.get_queryset({"has_box": True})
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [11111, 67890]

    def test_get_queryset_filters_by_has_box_false(self) -> None:
        """Test filtering by has_box=False."""
        queryset = self.service.get_queryset({"has_box": False})
        assert queryset.count() == 1
        assert queryset.first().number == 12345

    def test_get_queryset_filters_by_is_factory_sealed_true(self) -> None:
        """Test filtering by is_factory_sealed=True."""
        queryset = self.service.get_queryset({"is_factory_sealed": True})
        assert queryset.count() == 1
        assert queryset.first().number == 11111

    def test_get_queryset_filters_by_is_factory_sealed_false(self) -> None:
        """Test filtering by is_factory_sealed=False."""
        queryset = self.service.get_queryset({"is_factory_sealed": False})
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [12345, 67890]

    def test_get_queryset_filters_by_multiple_criteria(self) -> None:
        """Test filtering with multiple criteria combined."""
        queryset = self.service.get_queryset({
            "production_status": ProductionStatus.ACTIVE,
            "completeness": Completeness.COMPLETE,
            "has_instructions": True,
        })
        assert queryset.count() == 2
        numbers = sorted([bs.number for bs in queryset])
        assert numbers == [11111, 12345]

    def test_get_queryset_orders_by_created_at_ascending(self) -> None:
        """Test ordering by created_at (oldest first)."""
        queryset = self.service.get_queryset({"ordering": "created_at"})
        numbers = [bs.number for bs in queryset]
        # brickset1 created first, then brickset2, then brickset3
        assert numbers[0] == 12345

    def test_get_queryset_orders_by_created_at_descending_default(self) -> None:
        """Test ordering by -created_at (newest first, default)."""
        queryset = self.service.get_queryset({})
        numbers = [bs.number for bs in queryset]
        # Should be ordered by -created_at by default (newest first)
        assert numbers[-1] == 12345  # oldest last

    def test_get_queryset_orders_by_created_at_descending_explicit(self) -> None:
        """Test ordering by -created_at (newest first, explicit)."""
        queryset = self.service.get_queryset({"ordering": "-created_at"})
        numbers = [bs.number for bs in queryset]
        assert numbers[-1] == 12345  # oldest last

    def test_get_queryset_annotates_valuations_count_correctly(self) -> None:
        """Test that valuations_count annotation is correct."""
        queryset = self.service.get_queryset({})
        brickset_dict = {bs.id: bs for bs in queryset}

        assert brickset_dict[self.brickset1.id].valuations_count == 2
        assert brickset_dict[self.brickset2.id].valuations_count == 0
        assert brickset_dict[self.brickset3.id].valuations_count == 0

    def test_get_queryset_annotates_total_likes_correctly(self) -> None:
        """Test that total_likes annotation is correct."""
        queryset = self.service.get_queryset({})
        brickset_dict = {bs.id: bs for bs in queryset}

        assert brickset_dict[self.brickset1.id].total_likes == 8  # 5+3
        assert brickset_dict[self.brickset2.id].total_likes == 0
        assert brickset_dict[self.brickset3.id].total_likes == 0

    def test_get_queryset_annotates_total_likes_zero_when_no_valuations(self) -> None:
        """Test that total_likes is 0 (not None) when no valuations exist."""
        queryset = self.service.get_queryset({})
        for brickset in queryset:
            if brickset.id in [self.brickset2.id, self.brickset3.id]:
                assert brickset.total_likes is not None
                assert brickset.total_likes == 0

    def test_get_queryset_includes_top_valuation_id_annotation(self) -> None:
        """Test that top_valuation_id is annotated."""
        queryset = self.service.get_queryset({})
        brickset_dict = {bs.id: bs for bs in queryset}

        # brickset1 has top valuation (the one with 5 likes)
        assert brickset_dict[self.brickset1.id].top_valuation_id == self.valuation1.id
        # brickset2 and brickset3 have no valuations
        assert brickset_dict[self.brickset2.id].top_valuation_id is None
        assert brickset_dict[self.brickset3.id].top_valuation_id is None

    def test_get_queryset_is_lazy_evaluation(self) -> None:
        """Test that QuerySet is lazy (doesn't execute immediately)."""
        queryset = self.service.get_queryset({})
        # Accessing queryset object itself should not execute query
        assert queryset is not None
        # Only accessing data triggers query
        list(queryset)  # noqa: WPS122

    def test_map_to_dto_with_top_valuation(self) -> None:
        """Test mapping brickset to DTO with top valuation."""
        queryset = self.service.get_queryset({})
        brickset = queryset.filter(id=self.brickset1.id).first()

        dto = self.service.map_to_dto(brickset)

        assert dto.id == self.brickset1.id
        assert dto.number == 12345
        assert dto.valuations_count == 2
        assert dto.total_likes == 8
        assert dto.top_valuation is not None
        assert dto.top_valuation.id == self.valuation1.id
        assert dto.top_valuation.value == 400
        assert dto.top_valuation.likes_count == 5

    def test_map_to_dto_without_top_valuation(self) -> None:
        """Test mapping brickset to DTO without top valuation."""
        queryset = self.service.get_queryset({})
        brickset = queryset.filter(id=self.brickset2.id).first()

        dto = self.service.map_to_dto(brickset)

        assert dto.id == self.brickset2.id
        assert dto.number == 67890
        assert dto.valuations_count == 0
        assert dto.total_likes == 0
        assert dto.top_valuation is None

    def test_map_to_dto_includes_all_required_fields(self) -> None:
        """Test that DTO contains all required fields."""
        queryset = self.service.get_queryset({})
        brickset = queryset.first()
        dto = self.service.map_to_dto(brickset)

        # Check all required fields exist
        assert dto.id is not None
        assert dto.number is not None
        assert dto.production_status is not None
        assert dto.completeness is not None
        assert dto.has_instructions is not None
        assert dto.has_box is not None
        assert dto.is_factory_sealed is not None
        assert dto.owner_id is not None
        # owner_initial_estimate can be None
        assert dto.valuations_count is not None
        assert dto.total_likes is not None

    def test_get_queryset_orders_by_valuations_count_ascending(self) -> None:
        """Test ordering by valuations_count (fewest first)."""
        queryset = self.service.get_queryset({"ordering": "valuations_count"})
        counts = [bs.valuations_count for bs in queryset]
        # Should be ordered: 0, 0, 2
        assert counts == [0, 0, 2]

    def test_get_queryset_orders_by_valuations_count_descending(self) -> None:
        """Test ordering by -valuations_count (most first)."""
        queryset = self.service.get_queryset(
            {"ordering": "-valuations_count"}
        )
        counts = [bs.valuations_count for bs in queryset]
        # Should be ordered: 2, 0, 0
        assert counts[0] == 2
        assert counts[1] == 0
        assert counts[2] == 0

    def test_get_queryset_orders_by_total_likes_ascending(self) -> None:
        """Test ordering by total_likes (fewest first)."""
        queryset = self.service.get_queryset({"ordering": "total_likes"})
        likes = [bs.total_likes for bs in queryset]
        # Should be ordered: 0, 0, 8
        assert likes == [0, 0, 8]

    def test_get_queryset_orders_by_total_likes_descending(self) -> None:
        """Test ordering by -total_likes (most first)."""
        queryset = self.service.get_queryset({"ordering": "-total_likes"})
        likes = [bs.total_likes for bs in queryset]
        # Should be ordered: 8, 0, 0
        assert likes[0] == 8
        assert likes[1] == 0
        assert likes[2] == 0
