"""Tests for LikeValuationService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.models import BrickSet, Completeness, ProductionStatus
from datastore.domains.valuation_dto import CreateLikeCommand, LikeDTO
from valuation.exceptions import (
    LikeDuplicateError,
    LikeOwnValuationError,
    ValuationNotFoundError,
)
from valuation.models import Like, Valuation
from valuation.services.like_valuation_service import LikeValuationService


class LikeValuationServiceTests(TestCase):
    """Test LikeValuationService.execute() flow and error handling."""

    def setUp(self) -> None:
        """Create test users, BrickSet, and Valuation."""
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

        self.service = LikeValuationService()

    def test_execute_successfully_creates_like_and_returns_dto(self) -> None:
        """execute() successfully creates Like and returns LikeDTO."""
        command = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        result = self.service.execute(command)

        assert isinstance(result, LikeDTO)
        assert result.valuation_id == self.valuation.id
        assert result.user_id == self.liker.id
        assert result.created_at is not None

        # Verify Like was persisted to database
        like = Like.objects.get(user=self.liker, valuation=self.valuation)
        assert like.id is not None

    def test_execute_raises_valuation_not_found_error_for_nonexistent_valuation(
        self,
    ) -> None:
        """execute() raises ValuationNotFoundError when valuation doesn't exist."""
        command = CreateLikeCommand(
            valuation_id=999999,
            user_id=self.liker.id,
        )

        with self.assertRaises(ValuationNotFoundError) as exc_context:
            self.service.execute(command)

        assert exc_context.exception.valuation_id == 999999
        assert "Valuation with id 999999 not found" in str(exc_context.exception.message)

    def test_execute_raises_like_own_valuation_error_when_user_is_author(
        self,
    ) -> None:
        """execute() raises LikeOwnValuationError when user tries to like own valuation."""
        command = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.valuation_author.id,
        )

        with self.assertRaises(LikeOwnValuationError) as exc_context:
            self.service.execute(command)

        assert exc_context.exception.valuation_id == self.valuation.id
        assert "Cannot like your own valuation" in str(exc_context.exception.message)

    def test_execute_raises_like_duplicate_error_when_like_already_exists(
        self,
    ) -> None:
        """execute() raises LikeDuplicateError when user already liked valuation."""
        # Create first like
        first_command = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )
        self.service.execute(first_command)

        # Attempt to create duplicate like
        duplicate_command = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        with self.assertRaises(LikeDuplicateError) as exc_context:
            self.service.execute(duplicate_command)

        assert exc_context.exception.valuation_id == self.valuation.id
        assert exc_context.exception.user_id == self.liker.id
        assert "already exists" in str(exc_context.exception.message)

    def test_execute_preserves_created_at_timestamp(self) -> None:
        """execute() preserves created_at timestamp from database."""
        command = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )

        result = self.service.execute(command)

        # Verify timestamp is present and recent (within last 10 seconds)
        from datetime import datetime, timedelta, timezone
        now = datetime.now(tz=timezone.utc)
        time_diff = now - result.created_at
        assert timedelta(seconds=0) <= time_diff <= timedelta(seconds=10)

    def test_execute_allows_multiple_different_users_to_like_same_valuation(
        self,
    ) -> None:
        """execute() allows different users to like same valuation."""
        third_user = User.objects.create_user(
            username="third",
            email="third@example.com",
            password="thirdpass123",
        )

        # First user likes
        command1 = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=self.liker.id,
        )
        result1 = self.service.execute(command1)

        # Third user likes same valuation
        command2 = CreateLikeCommand(
            valuation_id=self.valuation.id,
            user_id=third_user.id,
        )
        result2 = self.service.execute(command2)

        assert result1.valuation_id == result2.valuation_id
        assert result1.user_id != result2.user_id
        assert Like.objects.filter(valuation=self.valuation).count() == 2
