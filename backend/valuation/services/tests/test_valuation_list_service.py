"""Tests for ValuationListService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet, Completeness, ProductionStatus
from datastore.domains.valuation_dto import ValuationListItemDTO
from valuation.models import Valuation
from valuation.services.valuation_list_service import ValuationListService


class ValuationListServiceTests(TestCase):
    """Test ValuationListService.get_queryset() and map_to_dto()."""

    def setUp(self) -> None:
        """Create test users, BrickSet and valuations."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass123",
        )
        self.brickset = BrickSet.objects.create(
            owner=self.owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.other_brickset = BrickSet.objects.create(
            owner=self.owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        self.service = ValuationListService()

    def test_get_queryset_returns_filtered_valuations(self) -> None:
        """get_queryset() returns valuations only for specified BrickSet."""
        valuation1 = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=450,
            currency="PLN",
            likes_count=5,
        )
        valuation2 = Valuation.valuations.create(
            user=self.user2,
            brickset=self.brickset,
            value=400,
            currency="PLN",
            likes_count=3,
        )
        # Different BrickSet - should not appear
        Valuation.valuations.create(
            user=self.user1,
            brickset=self.other_brickset,
            value=300,
            currency="PLN",
        )

        queryset = self.service.get_queryset(self.brickset.id)

        assert queryset.count() == 2
        valuation_ids = list(queryset.values_list("id", flat=True))
        assert valuation1.id in valuation_ids
        assert valuation2.id in valuation_ids

    def test_get_queryset_orders_by_likes_count_desc_then_created_at_asc(self) -> None:
        """get_queryset() orders by -likes_count, created_at."""
        valuation_low_likes = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=300,
            currency="PLN",
            likes_count=2,
        )
        valuation_high_likes = Valuation.valuations.create(
            user=self.user2,
            brickset=self.brickset,
            value=500,
            currency="PLN",
            likes_count=10,
        )
        valuation_no_likes = Valuation.valuations.create(
            user=self.owner,
            brickset=self.brickset,
            value=350,
            currency="PLN",
            likes_count=0,
        )

        queryset = self.service.get_queryset(self.brickset.id)

        ordered_ids = list(queryset.values_list("id", flat=True))
        # Most liked first
        assert ordered_ids[0] == valuation_high_likes.id
        assert ordered_ids[1] == valuation_low_likes.id
        assert ordered_ids[2] == valuation_no_likes.id

    def test_get_queryset_raises_error_for_nonexistent_brickset(self) -> None:
        """get_queryset() raises BrickSetNotFoundError for invalid ID."""
        nonexistent_id = 99999

        with self.assertRaises(BrickSetNotFoundError) as context:
            self.service.get_queryset(nonexistent_id)

        assert context.exception.brickset_id == nonexistent_id
        assert "not found" in str(context.exception.message).lower()

    def test_get_queryset_returns_empty_for_brickset_without_valuations(self) -> None:
        """get_queryset() returns empty QuerySet when BrickSet has no valuations."""
        # other_brickset has no valuations
        queryset = self.service.get_queryset(self.other_brickset.id)

        assert queryset.count() == 0

    def test_map_to_dto_returns_correct_valuation_list_item_dto(self) -> None:
        """map_to_dto() converts Valuation to ValuationListItemDTO correctly."""
        valuation = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=450,
            currency="PLN",
            comment="Excellent condition",
            likes_count=7,
        )

        result = self.service.map_to_dto(valuation)

        assert isinstance(result, ValuationListItemDTO)
        assert result.id == valuation.id
        assert result.user_id == self.user1.id
        assert result.value == 450
        assert result.currency == "PLN"
        assert result.comment == "Excellent condition"
        assert result.likes_count == 7
        assert result.created_at == valuation.created_at

    def test_map_to_dto_handles_null_comment(self) -> None:
        """map_to_dto() correctly handles None comment."""
        valuation = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=300,
            currency="EUR",
            comment=None,
            likes_count=0,
        )

        result = self.service.map_to_dto(valuation)

        assert result.comment is None

    def test_map_to_dto_excludes_brickset_id_and_updated_at(self) -> None:
        """map_to_dto() does not include brickset_id or updated_at in DTO."""
        valuation = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=500,
            currency="PLN",
        )

        result = self.service.map_to_dto(valuation)

        # Verify DTO doesn't have these attributes
        assert not hasattr(result, "brickset_id")
        assert not hasattr(result, "updated_at")
        # But has required fields
        assert hasattr(result, "id")
        assert hasattr(result, "user_id")
        assert hasattr(result, "created_at")
