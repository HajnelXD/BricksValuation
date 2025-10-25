"""Tests for UnlikeValuationService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.models import BrickSet, Completeness, ProductionStatus
from datastore.domains.valuation_dto import UnlikeValuationCommand
from valuation.exceptions import LikeNotFoundError
from valuation.models import Like, Valuation
from valuation.services.unlike_valuation_service import UnlikeValuationService


class UnlikeValuationServiceTests(TestCase):
    """Test UnlikeValuationService.execute() flow and error handling."""

    def setUp(self) -> None:
        """Create test users, BrickSet, Valuation, and Like."""
        self.valuation_author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="authorpass123",
        )
        self.liker = User.objects.create_user(
            username="liker",
            email="liker@example.com",
            password="likerpass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="otherpass123",
        )
        self.brickset_owner = User.objects.create_user(
            username="brickset_owner",
            email="brickset_owner@example.com",
            password="ownerpass123",
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

        self.valuation = Valuation.valuations.create(
            user=self.valuation_author,
            brickset=self.brickset,
            value=500,
            currency="PLN",
            comment="Test valuation",
        )

        # Create a like for the liker
        self.like = Like.objects.create(
            user=self.liker,
            valuation=self.valuation,
        )

        self.service = UnlikeValuationService()

    def test_execute_successfully_deletes_like_when_exists(self) -> None:
        """execute() successfully deletes Like from database."""
        like_id = self.like.id
        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        result = self.service.execute(command)

        assert result is None
        assert not Like.objects.filter(pk=like_id).exists()

    def test_execute_raises_like_not_found_error_when_like_does_not_exist(
        self,
    ) -> None:
        """execute() raises LikeNotFoundError when Like doesn't exist."""
        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.other_user.id,  # This user never liked
        )

        with self.assertRaises(LikeNotFoundError) as exc_context:
            self.service.execute(command)

        assert exc_context.exception.valuation_id == self.valuation.id
        assert exc_context.exception.user_id == self.other_user.id
        assert "not found" in str(exc_context.exception.message)

    def test_execute_raises_like_not_found_error_for_different_user(
        self,
    ) -> None:
        """execute() raises LikeNotFoundError when different user attempts to unlike.

        Implicit authorization: user can only delete their own like.
        """
        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.other_user.id,  # Different user than who created the like
        )

        with self.assertRaises(LikeNotFoundError) as exc_context:
            self.service.execute(command)

        assert exc_context.exception.valuation_id == self.valuation.id
        assert exc_context.exception.user_id == self.other_user.id

        # Original like should still exist
        assert Like.objects.filter(
            user=self.liker,
            valuation=self.valuation,
        ).exists()

    def test_execute_returns_none(self) -> None:
        """execute() returns None (DELETE endpoint returns 204 No Content)."""
        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        result = self.service.execute(command)

        assert result is None

    def test_execute_idempotent_raises_error_on_second_call(self) -> None:
        """execute() is not idempotent - second call raises LikeNotFoundError.

        REST DELETE convention: after successful delete, subsequent DELETE
        returns 404 (not idempotent like most DELETE operations).
        """
        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        # First call succeeds
        self.service.execute(command)
        assert not Like.objects.filter(
            user=self.liker,
            valuation=self.valuation,
        ).exists()

        # Second call raises LikeNotFoundError
        with self.assertRaises(LikeNotFoundError):
            self.service.execute(command)

    def test_execute_does_not_affect_other_users_likes(self) -> None:
        """execute() only deletes the specific (valuation, user) Like.

        Other users' likes on same valuation remain unchanged.
        """
        # Create another like from other_user
        other_like = Like.objects.create(
            user=self.other_user,
            valuation=self.valuation,
        )

        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        self.service.execute(command)

        # Liker's like should be deleted
        assert not Like.objects.filter(
            user=self.liker,
            valuation=self.valuation,
        ).exists()

        # Other user's like should still exist
        assert Like.objects.filter(pk=other_like.id).exists()

    def test_execute_deletes_only_target_like_not_all_likes(self) -> None:
        """execute() deletes only the target Like, not all likes on valuation."""
        # Create multiple likes on same valuation
        third_user = User.objects.create_user(
            username="third",
            email="third@example.com",
            password="thirdpass123",
        )
        third_like = Like.objects.create(
            user=third_user,
            valuation=self.valuation,
        )

        initial_like_count = Like.objects.filter(
            valuation=self.valuation,
        ).count()

        command = UnlikeValuationCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        self.service.execute(command)

        # One like deleted, but others remain
        final_like_count = Like.objects.filter(
            valuation=self.valuation,
        ).count()
        assert final_like_count == initial_like_count - 1
        assert Like.objects.filter(pk=third_like.id).exists()
