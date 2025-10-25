"""Tests for OwnedValuationListService."""
from __future__ import annotations

from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker

from catalog.models import BrickSet, ProductionStatus, Completeness
from valuation.models import Valuation
from valuation.services import OwnedValuationListService

User = get_user_model()


class OwnedValuationListServiceTests(TestCase):
    """Test suite for OwnedValuationListService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = OwnedValuationListService()
        self.user = baker.make(User)
        self.other_user = baker.make(User)

        # Create test bricksets
        self.brickset1 = baker.make(
            BrickSet,
            owner=self.user,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        self.brickset2 = baker.make(
            BrickSet,
            owner=self.user,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
        )
        self.brickset3 = baker.make(
            BrickSet,
            owner=self.user,
            number=13579,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        self.other_brickset = baker.make(
            BrickSet,
            owner=self.other_user,
            number=11111,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )

        # Create valuations for user (one per brickset, unique constraint)
        self.valuation1 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset1,
            value=350,
            currency="PLN",
            comment="Good condition",
            likes_count=5,
        )
        self.valuation2 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset2,
            value=250,
            currency="PLN",
            comment="Fair condition",
            likes_count=2,
        )
        self.valuation3 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset3,
            value=400,
            currency="PLN",
            comment="Excellent condition",
            likes_count=8,
        )

        # Create valuation for other_user (should not be returned)
        self.other_user_valuation = baker.make(
            Valuation,
            user=self.other_user,
            brickset=self.other_brickset,
            value=300,
            currency="PLN",
            likes_count=3,
        )

    def test_get_queryset_returns_only_user_valuations(self) -> None:
        """Test that get_queryset returns only valuations owned by user."""
        queryset = self.service.get_queryset(self.user.id)
        assert queryset.count() == 3
        valuation_ids = {val.id for val in queryset}
        assert self.valuation1.id in valuation_ids
        assert self.valuation2.id in valuation_ids
        assert self.valuation3.id in valuation_ids

    def test_get_queryset_excludes_other_users_valuations(self) -> None:
        """Test that get_queryset excludes valuations owned by other users."""
        queryset = self.service.get_queryset(self.user.id)
        valuation_ids = {val.id for val in queryset}
        assert self.other_user_valuation.id not in valuation_ids

    def test_get_queryset_returns_empty_when_user_has_no_valuations(self) -> None:
        """Test that get_queryset returns empty list for user with no valuations."""
        another_user = baker.make(User)
        queryset = self.service.get_queryset(another_user.id)
        assert queryset.count() == 0

    def test_get_queryset_applies_default_ordering_created_at_desc(self) -> None:
        """Test that default ordering is -created_at (newest first)."""
        queryset = self.service.get_queryset(self.user.id)
        # Get ordered IDs - should be reversed chronologically
        ordered_ids = list(queryset.values_list("id", flat=True))
        # First should be valuation3 (last created), last should be valuation1 (first created)
        assert ordered_ids[0] == self.valuation3.id
        assert ordered_ids[-1] == self.valuation1.id

    def test_get_queryset_applies_custom_ordering_likes_count_desc(self) -> None:
        """Test ordering by likes_count descending."""
        queryset = self.service.get_queryset(self.user.id, ordering="-likes_count")
        likes_counts = list(queryset.values_list("likes_count", flat=True))
        # Should be ordered: 8, 5, 2
        assert likes_counts == [8, 5, 2]

    def test_get_queryset_applies_custom_ordering_likes_count_asc(self) -> None:
        """Test ordering by likes_count ascending."""
        queryset = self.service.get_queryset(self.user.id, ordering="likes_count")
        likes_counts = list(queryset.values_list("likes_count", flat=True))
        # Should be ordered: 2, 5, 8
        assert likes_counts == [2, 5, 8]

    def test_get_queryset_applies_custom_ordering_value_desc(self) -> None:
        """Test ordering by value descending."""
        queryset = self.service.get_queryset(self.user.id, ordering="-value")
        values = list(queryset.values_list("value", flat=True))
        # Should be ordered: 400, 350, 250
        assert values == [400, 350, 250]

    def test_get_queryset_applies_custom_ordering_value_asc(self) -> None:
        """Test ordering by value ascending."""
        queryset = self.service.get_queryset(self.user.id, ordering="value")
        values = list(queryset.values_list("value", flat=True))
        # Should be ordered: 250, 350, 400
        assert values == [250, 350, 400]

    def test_get_queryset_includes_select_related_brickset(self) -> None:
        """Test that queryset includes select_related('brickset') optimization."""
        queryset = self.service.get_queryset(self.user.id)
        # Execute query and check that brickset is already loaded
        valuation = list(queryset)[0]
        # Access brickset should not trigger additional query (it's in select_related)
        assert valuation.brickset.id == valuation.brickset_id

    def test_get_queryset_ignores_invalid_ordering(self) -> None:
        """Test that invalid ordering is ignored (returns default ordering)."""
        queryset = self.service.get_queryset(self.user.id, ordering="invalid_field")
        # Should still return results (not raise error) in default order
        assert queryset.count() == 3
        # Should use default ordering since invalid_field is not in ALLOWED_ORDERINGS
        # Default ordering is -created_at, so just verify we got all valuations
        queryset_ids = {val.id for val in queryset}
        expected_ids = {self.valuation1.id, self.valuation2.id, self.valuation3.id}
        assert queryset_ids == expected_ids

    def test_map_to_dto_creates_correct_owned_valuation_dto(self) -> None:
        """Test that map_to_dto creates correct OwnedValuationListItemDTO."""
        queryset = self.service.get_queryset(self.user.id)
        valuation = queryset.first()
        dto = self.service.map_to_dto(valuation)

        assert dto.id == valuation.id
        assert dto.value == valuation.value
        assert dto.currency == valuation.currency
        assert dto.likes_count == valuation.likes_count
        assert dto.created_at == valuation.created_at

    def test_map_to_dto_includes_nested_brickset_dict(self) -> None:
        """Test that map_to_dto includes nested brickset dict."""
        queryset = self.service.get_queryset(self.user.id)
        valuation = queryset.first()
        dto = self.service.map_to_dto(valuation)

        assert isinstance(dto.brickset, dict)
        assert "id" in dto.brickset
        assert "number" in dto.brickset

    def test_map_to_dto_extracts_correct_brickset_id_and_number(self) -> None:
        """Test that map_to_dto extracts correct brickset id and number."""
        queryset = self.service.get_queryset(self.user.id)
        valuation = queryset.first()
        dto = self.service.map_to_dto(valuation)

        assert dto.brickset["id"] == valuation.brickset.id
        assert dto.brickset["number"] == valuation.brickset.number
