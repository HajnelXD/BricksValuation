"""Tests for LikeListService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.models import BrickSet, Completeness, ProductionStatus
from datastore.domains.valuation_dto import LikeListItemDTO
from valuation.exceptions import ValuationNotFoundError
from valuation.models import Like, Valuation
from valuation.services.like_list_service import LikeListService


class LikeListServiceTests(TestCase):
    """Test LikeListService.get_queryset() and map_to_dto()."""

    def setUp(self) -> None:
        """Create test users, BrickSet and Valuation with likes."""
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
        self.user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="pass123",
        )
        self.valuation_author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="pass123",
        )
        self.other_author = User.objects.create_user(
            username="other_author",
            email="other_author@example.com",
            password="pass123",
        )
        self.brickset_owner = User.objects.create_user(
            username="brickset_owner",
            email="brickset_owner@example.com",
            password="pass123",
        )
        self.brickset = BrickSet.objects.create(
            owner=self.brickset_owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.other_brickset = BrickSet.objects.create(
            owner=self.brickset_owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        self.valuation = Valuation.valuations.create(
            user=self.valuation_author,
            brickset=self.brickset,
            value=450,
            currency="PLN",
        )
        self.other_valuation = Valuation.valuations.create(
            user=self.other_author,
            brickset=self.other_brickset,
            value=500,
            currency="PLN",
        )
        self.service = LikeListService()

    def test_get_queryset_returns_filtered_likes(self) -> None:
        """get_queryset() returns likes only for specified Valuation."""
        like1 = Like.objects.create(user=self.user1, valuation=self.valuation)
        like2 = Like.objects.create(user=self.user2, valuation=self.valuation)
        # Different Valuation - should not appear
        Like.objects.create(user=self.user1, valuation=self.other_valuation)

        queryset = self.service.get_queryset(self.valuation.id)

        assert queryset.count() == 2
        like_ids = list(queryset.values_list("id", flat=True))
        assert like1.id in like_ids
        assert like2.id in like_ids

    def test_get_queryset_orders_by_created_at_descending(self) -> None:
        """get_queryset() orders by -created_at (newest first)."""
        like1 = Like.objects.create(user=self.user1, valuation=self.valuation)
        like2 = Like.objects.create(user=self.user2, valuation=self.valuation)
        like3 = Like.objects.create(user=self.user3, valuation=self.valuation)

        queryset = self.service.get_queryset(self.valuation.id)

        ordered_ids = list(queryset.values_list("id", flat=True))
        # Newest first (like3 created last)
        assert ordered_ids[0] == like3.id
        assert ordered_ids[1] == like2.id
        assert ordered_ids[2] == like1.id

    def test_get_queryset_raises_error_for_nonexistent_valuation(self) -> None:
        """get_queryset() raises ValuationNotFoundError for invalid ID."""
        nonexistent_id = 99999

        with self.assertRaises(ValuationNotFoundError) as context:
            self.service.get_queryset(nonexistent_id)

        assert context.exception.valuation_id == nonexistent_id
        assert "not found" in str(context.exception.message).lower()

    def test_get_queryset_returns_empty_for_valuation_without_likes(self) -> None:
        """get_queryset() returns empty QuerySet when Valuation has no likes."""
        # other_valuation has no likes
        queryset = self.service.get_queryset(self.other_valuation.id)

        assert queryset.count() == 0

    def test_map_to_dto_returns_correct_like_list_item_dto(self) -> None:
        """map_to_dto() converts Like to LikeListItemDTO correctly."""
        like = Like.objects.create(user=self.user1, valuation=self.valuation)

        result = self.service.map_to_dto(like)

        assert isinstance(result, LikeListItemDTO)
        assert result.user_id == self.user1.id
        assert result.created_at == like.created_at

    def test_map_to_dto_excludes_valuation_id_and_updated_at(self) -> None:
        """map_to_dto() does not include valuation_id or updated_at in DTO."""
        like = Like.objects.create(user=self.user1, valuation=self.valuation)

        result = self.service.map_to_dto(like)

        # Verify DTO doesn't have these attributes
        assert not hasattr(result, "valuation_id")
        assert not hasattr(result, "updated_at")
        # But has required fields
        assert hasattr(result, "user_id")
        assert hasattr(result, "created_at")
