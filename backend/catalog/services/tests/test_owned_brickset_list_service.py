"""Tests for OwnedBrickSetListService."""
from __future__ import annotations

from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker

from catalog.models import BrickSet, ProductionStatus, Completeness
from catalog.services.owned_brickset_list_service import OwnedBrickSetListService
from valuation.models import Valuation

User = get_user_model()


class OwnedBrickSetListServiceTests(TestCase):
    """Test suite for OwnedBrickSetListService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = OwnedBrickSetListService()
        self.owner = baker.make(User)
        self.other_user = baker.make(User)

        # Create test bricksets for owner
        self.owned_brickset1 = baker.make(
            BrickSet,
            owner=self.owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=350,
        )
        self.owned_brickset2 = baker.make(
            BrickSet,
            owner=self.owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=None,
        )

        # Create brickset for other user (should not be returned)
        self.other_brickset = baker.make(
            BrickSet,
            owner=self.other_user,
            number=11111,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=True,
            owner_initial_estimate=500,
        )

        # Create valuations: owner has 2 on brickset1, other_user has 1 on brickset1
        self.owner_valuation = baker.make(
            Valuation,
            user=self.owner,
            brickset=self.owned_brickset1,
            value=380,
            currency="PLN",
            comment="Good condition",
            likes_count=0,  # No likes on owner's valuation
        )
        self.other_user_valuation = baker.make(
            Valuation,
            user=self.other_user,
            brickset=self.owned_brickset1,
            value=400,
            currency="PLN",
            comment="Nice set",
            likes_count=5,
        )

    def test_get_queryset_returns_only_owner_bricksets(self) -> None:
        """Test that get_queryset returns only bricksets owned by user."""
        queryset = self.service.get_queryset(self.owner.id)
        assert queryset.count() == 2
        brickset_ids = {bs.id for bs in queryset}
        assert self.owned_brickset1.id in brickset_ids
        assert self.owned_brickset2.id in brickset_ids

    def test_get_queryset_excludes_other_users_bricksets(self) -> None:
        """Test that get_queryset excludes bricksets owned by other users."""
        queryset = self.service.get_queryset(self.owner.id)
        brickset_ids = {bs.id for bs in queryset}
        assert self.other_brickset.id not in brickset_ids

    def test_get_queryset_returns_empty_when_user_has_no_bricksets(self) -> None:
        """Test that get_queryset returns empty list for user with no bricksets."""
        another_user = baker.make(User)
        queryset = self.service.get_queryset(another_user.id)
        assert queryset.count() == 0

    def test_get_queryset_adds_valuations_count_annotation(self) -> None:
        """Test that valuations_count annotation is added."""
        queryset = self.service.get_queryset(self.owner.id)
        brickset_dict = {bs.id: bs for bs in queryset}

        # owned_brickset1 has 2 valuations (owner + other_user)
        assert brickset_dict[self.owned_brickset1.id].valuations_count == 2
        # owned_brickset2 has 0 valuations
        assert brickset_dict[self.owned_brickset2.id].valuations_count == 0

    def test_get_queryset_adds_total_likes_annotation(self) -> None:
        """Test that total_likes annotation is added."""
        queryset = self.service.get_queryset(self.owner.id)
        brickset_dict = {bs.id: bs for bs in queryset}

        # owned_brickset1: owner valuation has 0 likes, other_user has 5 likes = 5 total
        assert brickset_dict[self.owned_brickset1.id].total_likes == 5
        # owned_brickset2 has 0 total likes
        assert brickset_dict[self.owned_brickset2.id].total_likes == 0

    def test_get_queryset_total_likes_zero_when_no_valuations(self) -> None:
        """Test that total_likes is 0 (not None) when no valuations exist."""
        queryset = self.service.get_queryset(self.owner.id)
        for brickset in queryset:
            if brickset.id == self.owned_brickset2.id:
                assert brickset.total_likes is not None
                assert brickset.total_likes == 0

    def test_get_queryset_applies_default_ordering_created_at_desc(self) -> None:
        """Test that default ordering is -created_at (newest first)."""
        queryset = self.service.get_queryset(self.owner.id)
        numbers = [bs.number for bs in queryset]
        # owned_brickset1 created first, owned_brickset2 created second
        # Default ordering is -created_at, so newest (owned_brickset2) should be first
        assert numbers[0] == 67890  # owned_brickset2 (newer)
        assert numbers[1] == 12345  # owned_brickset1 (older)

    def test_get_queryset_applies_custom_ordering_created_at_asc(self) -> None:
        """Test custom ordering by created_at (oldest first)."""
        queryset = self.service.get_queryset(self.owner.id, "created_at")
        numbers = [bs.number for bs in queryset]
        # Oldest first
        assert numbers[0] == 12345  # owned_brickset1 (older)
        assert numbers[1] == 67890  # owned_brickset2 (newer)

    def test_get_queryset_applies_custom_ordering_valuations_count_desc(self) -> None:
        """Test custom ordering by -valuations_count (most valuations first)."""
        queryset = self.service.get_queryset(self.owner.id, "-valuations_count")
        counts = [bs.valuations_count for bs in queryset]
        # Should be ordered: 2, 0 (most first)
        assert counts[0] == 2
        assert counts[1] == 0

    def test_get_queryset_applies_custom_ordering_total_likes_asc(self) -> None:
        """Test custom ordering by total_likes (fewest likes first)."""
        queryset = self.service.get_queryset(self.owner.id, "total_likes")
        likes = [bs.total_likes for bs in queryset]
        # Should be ordered: 0, 5 (fewest first)
        assert likes[0] == 0
        assert likes[1] == 5

    def test_map_to_dto_creates_correct_owned_brickset_dto(self) -> None:
        """Test that map_to_dto creates correct OwnedBrickSetListItemDTO."""
        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.filter(id=self.owned_brickset1.id).first()

        dto = self.service.map_to_dto(brickset)

        assert dto.id == self.owned_brickset1.id
        assert dto.number == 12345
        assert dto.production_status == ProductionStatus.ACTIVE
        assert dto.completeness == Completeness.COMPLETE
        assert dto.valuations_count == 2
        assert dto.total_likes == 5
        assert hasattr(dto, "editable")

    def test_map_to_dto_sets_editable_true_when_rb01_satisfied(self) -> None:
        """Test RB-01: editable=True when no other users AND owner has 0 likes.

        RB-01 rule: BrickSet is editable if:
        - No valuations from other users exist AND
        - Owner's valuation (if exists) has 0 likes
        """
        # Create fresh brickset with only owner valuation (0 likes)
        brickset_fresh = baker.make(
            BrickSet,
            owner=self.owner,
            number=99999,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        baker.make(
            Valuation,
            user=self.owner,
            brickset=brickset_fresh,
            value=300,
            currency="PLN",
            likes_count=0,  # 0 likes
        )

        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.filter(id=brickset_fresh.id).first()
        dto = self.service.map_to_dto(brickset)

        assert dto.editable is True

    def test_map_to_dto_sets_editable_false_when_other_users_valuations_exist(
        self,
    ) -> None:
        """Test RB-01: editable=False when other users' valuations exist."""
        # owned_brickset1 already has other_user_valuation
        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.filter(id=self.owned_brickset1.id).first()
        dto = self.service.map_to_dto(brickset)

        assert dto.editable is False

    def test_map_to_dto_sets_editable_false_when_owner_valuation_has_likes(
        self,
    ) -> None:
        """Test RB-01: editable=False when owner's valuation has likes."""
        # Create brickset with only owner valuation but with likes
        brickset_with_likes = baker.make(
            BrickSet,
            owner=self.owner,
            number=88888,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        baker.make(
            Valuation,
            user=self.owner,
            brickset=brickset_with_likes,
            value=300,
            currency="PLN",
            likes_count=5,  # Has likes!
        )

        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.filter(id=brickset_with_likes.id).first()
        dto = self.service.map_to_dto(brickset)

        assert dto.editable is False

    def test_is_editable_returns_true_when_no_valuations(self) -> None:
        """Test RB-01: editable=True when brickset has no valuations (edge case)."""
        # owned_brickset2 has no valuations
        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.filter(id=self.owned_brickset2.id).first()

        is_editable = self.service._is_editable(brickset)

        assert is_editable is True

    def test_is_editable_works_with_prefetched_valuations(self) -> None:
        """Test that _is_editable works with prefetched valuations."""
        queryset = (
            BrickSet.bricksets
            .filter(owner_id=self.owner.id)
            .prefetch_related("valuations")
        )
        brickset = queryset.filter(id=self.owned_brickset1.id).first()

        is_editable = self.service._is_editable(brickset)

        # owned_brickset1 has other_user valuations, so not editable
        assert is_editable is False

    def test_map_to_dto_includes_all_required_fields(self) -> None:
        """Test that OwnedBrickSetListItemDTO contains all required fields."""
        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.first()
        dto = self.service.map_to_dto(brickset)

        # Check all required fields exist
        assert dto.id is not None
        assert dto.number is not None
        assert dto.production_status is not None
        assert dto.completeness is not None
        assert dto.valuations_count is not None
        assert dto.total_likes is not None
        assert dto.editable is not None

    def test_map_to_dto_returns_dto_object_type(self) -> None:
        """Test that map_to_dto returns correct DTO type."""
        from datastore.domains.catalog_dto import OwnedBrickSetListItemDTO

        queryset = self.service.get_queryset(self.owner.id)
        brickset = queryset.first()
        dto = self.service.map_to_dto(brickset)

        assert isinstance(dto, OwnedBrickSetListItemDTO)

    def test_get_queryset_is_lazy_evaluation(self) -> None:
        """Test that QuerySet is lazy (doesn't execute immediately)."""
        queryset = self.service.get_queryset(self.owner.id)
        # Accessing queryset object itself should not execute query
        assert queryset is not None
        # Only accessing data triggers query
        list(queryset)  # noqa: WPS122
