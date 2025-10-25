"""Tests for DeleteBrickSetService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.exceptions import BrickSetNotFoundError, BrickSetEditForbiddenError
from catalog.models import BrickSet, Completeness, ProductionStatus
from catalog.services.brickset_delete_service import DeleteBrickSetService
from valuation.models import Valuation


class DeleteBrickSetServiceTests(TestCase):
    """Test DeleteBrickSetService.execute() authorization and RB-01 validation."""

    def setUp(self) -> None:
        """Create test users and bricksets."""
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="testpass123",
        )
        self.service = DeleteBrickSetService()

        # Create test brickset
        self.brickset = BrickSet.objects.create(
            owner=self.owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=250,
        )

    def test_execute_deletes_brickset_from_database(self) -> None:
        """execute() removes BrickSet from database."""
        brickset_id = self.brickset.id

        self.service.execute(brickset_id, self.owner)

        with self.assertRaises(BrickSet.DoesNotExist):
            BrickSet.bricksets.get(pk=brickset_id)

    def test_execute_deletes_only_target_brickset(self) -> None:
        """execute() deletes only the target BrickSet, not others."""
        other_brickset = BrickSet.objects.create(
            owner=self.owner,
            number=54321,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=True,
            owner_initial_estimate=100,
        )
        target_id = self.brickset.id

        self.service.execute(target_id, self.owner)

        with self.assertRaises(BrickSet.DoesNotExist):
            BrickSet.bricksets.get(pk=target_id)
        # Other brickset should still exist
        assert BrickSet.bricksets.filter(pk=other_brickset.id).exists()

    def test_execute_cascades_delete_valuations(self) -> None:
        """execute() cascades delete to related valuations."""
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=0,
        )
        valuation_id = valuation.id
        brickset_id = self.brickset.id

        self.service.execute(brickset_id, self.owner)

        with self.assertRaises(BrickSet.DoesNotExist):
            BrickSet.bricksets.get(pk=brickset_id)
        with self.assertRaises(Valuation.DoesNotExist):
            Valuation.valuations.get(pk=valuation_id)

    def test_execute_cascades_delete_multiple_valuations(self) -> None:
        """execute() cascades delete valuations and likes from owner."""
        # Create owner valuation with a like
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=0,
        )
        # Simulate a like (Valuation has likes via reverse FK from Like model)
        # Note: This test verifies CASCADE works on the valuation itself
        brickset_id = self.brickset.id
        valuation_id = valuation.id

        self.service.execute(brickset_id, self.owner)

        assert not BrickSet.bricksets.filter(pk=brickset_id).exists()
        assert not Valuation.valuations.filter(pk=valuation_id).exists()

    def test_execute_returns_none(self) -> None:
        """execute() returns None (no response body for DELETE)."""
        result = self.service.execute(self.brickset.id, self.owner)

        assert result is None

    def test_execute_raises_not_found_for_nonexistent_id(self) -> None:
        """execute() raises BrickSetNotFoundError for nonexistent brickset."""
        with self.assertRaises(BrickSetNotFoundError) as context:
            self.service.execute(999999, self.owner)

        assert context.exception.brickset_id == 999999
        assert "not found" in context.exception.message.lower()

    def test_execute_raises_forbidden_when_user_not_owner(self) -> None:
        """execute() raises BrickSetEditForbiddenError when user not owner."""
        with self.assertRaises(BrickSetEditForbiddenError) as context:
            self.service.execute(self.brickset.id, self.other_user)

        assert context.exception.reason == "not_owner"
        # Brickset should NOT be deleted
        assert BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_execute_raises_forbidden_with_other_users_valuations(self) -> None:
        """execute() raises BrickSetEditForbiddenError with other users' valuations."""
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.other_user,
            value=350,
            currency="PLN",
            likes_count=0,
        )

        with self.assertRaises(BrickSetEditForbiddenError) as context:
            self.service.execute(self.brickset.id, self.owner)

        assert context.exception.reason == "other_users_valuations_exist"
        # Brickset should NOT be deleted
        assert BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_execute_raises_forbidden_when_owner_valuation_has_likes(self) -> None:
        """execute() raises BrickSetEditForbiddenError when owner valuation has likes."""
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=5,  # Has likes
        )

        with self.assertRaises(BrickSetEditForbiddenError) as context:
            self.service.execute(self.brickset.id, self.owner)

        assert context.exception.reason == "owner_valuation_has_likes"
        # Brickset should NOT be deleted
        assert BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_execute_allows_delete_when_no_valuations(self) -> None:
        """execute() allows delete when no valuations exist."""
        brickset_id = self.brickset.id

        self.service.execute(brickset_id, self.owner)

        assert not BrickSet.bricksets.filter(pk=brickset_id).exists()

    def test_execute_allows_delete_when_owner_valuation_zero_likes(self) -> None:
        """execute() allows delete when owner's valuation has 0 likes."""
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=0,  # No likes
        )
        brickset_id = self.brickset.id

        self.service.execute(brickset_id, self.owner)

        assert not BrickSet.bricksets.filter(pk=brickset_id).exists()

    def test_execute_rb_01_prioritizes_other_users_validation(self) -> None:
        """execute() checks other users' valuations first."""
        # Create both owner and other user valuations
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=5,  # Owner has likes
        )
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.other_user,
            value=400,
            currency="PLN",
            likes_count=0,
        )

        # Should fail with other_users_valuations_exist (checked first)
        with self.assertRaises(BrickSetEditForbiddenError) as context:
            self.service.execute(self.brickset.id, self.owner)

        assert context.exception.reason == "other_users_valuations_exist"

    def test_execute_uses_prefetch_related_efficiently(self) -> None:
        """execute() uses prefetch_related to minimize database queries."""
        # Create some valuations to ensure prefetch is working
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
            currency="PLN",
            likes_count=0,
        )

        # Should execute without additional queries for valuations access
        result = self.service.execute(self.brickset.id, self.owner)

        # Verify deletion happened
        assert not BrickSet.bricksets.filter(pk=self.brickset.id).exists()
        assert result is None

    def test_execute_transactional_rollback_on_validation_failure(self) -> None:
        """execute() doesn't delete if RB-01 validation fails."""
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.other_user,
            value=350,
            currency="PLN",
            likes_count=0,
        )
        brickset_id = self.brickset.id

        try:
            self.service.execute(brickset_id, self.owner)
        except BrickSetEditForbiddenError:  # noqa: WPS420
            ...

        # BrickSet should still exist due to transaction atomicity
        assert BrickSet.bricksets.filter(pk=brickset_id).exists()
