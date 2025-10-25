"""Tests for CreateValuationService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet, Completeness, ProductionStatus
from datastore.domains.valuation_dto import CreateValuationCommand, ValuationDTO
from valuation.exceptions import ValuationDuplicateError
from valuation.models import Valuation
from valuation.services.valuation_create_service import CreateValuationService


class CreateValuationServiceTests(TestCase):
    """Test CreateValuationService.execute() flow and error handling."""

    def setUp(self) -> None:
        """Create test user and BrickSet."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="ownerpass123",
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
        self.service = CreateValuationService()

    def test_execute_creates_valuation_with_all_fields(self) -> None:
        """execute() successfully creates Valuation with all fields."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=450,
            currency="PLN",
            comment="Looks complete and in great condition",
        )

        result = self.service.execute(command, self.user)

        assert isinstance(result, ValuationDTO)
        assert result.brickset_id == self.brickset.id
        assert result.value == 450
        assert result.currency == "PLN"
        assert result.comment == "Looks complete and in great condition"
        assert result.user_id == self.user.id
        assert Valuation.valuations.filter(user=self.user, brickset=self.brickset).exists()

    def test_execute_creates_valuation_without_comment(self) -> None:
        """execute() creates Valuation with comment=None."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=300,
            currency="EUR",
            comment=None,
        )

        result = self.service.execute(command, self.user)

        assert result.comment is None
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.comment is None

    def test_execute_uses_default_currency_when_none(self) -> None:
        """execute() defaults currency to PLN when None."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=500,
            currency=None,
            comment="Test",
        )

        result = self.service.execute(command, self.user)

        assert result.currency == "PLN"
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.currency == "PLN"

    def test_execute_sets_correct_user(self) -> None:
        """execute() sets user to provided user."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=250,
        )

        result = self.service.execute(command, self.user)

        assert result.user_id == self.user.id
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.user == self.user

    def test_execute_returns_valuation_dto(self) -> None:
        """execute() returns ValuationDTO."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=400,
        )

        result = self.service.execute(command, self.user)

        assert isinstance(result, ValuationDTO)

    def test_execute_dto_has_correct_fields(self) -> None:
        """execute() returns DTO with all required fields."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=350,
            currency="USD",
            comment="Good shape",
        )

        result = self.service.execute(command, self.user)

        assert result.id is not None
        assert result.brickset_id == self.brickset.id
        assert result.user_id == self.user.id
        assert result.value == 350
        assert result.currency == "USD"
        assert result.comment == "Good shape"
        assert result.likes_count == 0
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_execute_persists_valuation_to_database(self) -> None:
        """execute() persists Valuation to database."""
        initial_count = Valuation.valuations.count()
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=275,
        )

        self.service.execute(command, self.user)

        assert Valuation.valuations.count() == initial_count + 1

    def test_execute_raises_brickset_not_found_error_for_invalid_id(self) -> None:
        """execute() raises BrickSetNotFoundError for non-existent BrickSet."""
        command = CreateValuationCommand(
            brickset_id=99999,
            value=300,
        )

        with self.assertRaises(BrickSetNotFoundError) as context:
            self.service.execute(command, self.user)

        assert context.exception.brickset_id == 99999
        assert "not found" in context.exception.message.lower()

    def test_execute_raises_duplicate_error_for_same_user_brickset(self) -> None:
        """execute() raises ValuationDuplicateError for duplicate user-brickset pair."""
        # Create first valuation
        command1 = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=400,
        )
        self.service.execute(command1, self.user)

        # Try to create second valuation for same user and brickset
        command2 = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=450,
        )

        with self.assertRaises(ValuationDuplicateError) as context:
            self.service.execute(command2, self.user)

        assert context.exception.constraint == "valuation_unique_user_brickset"
        assert "already exists" in context.exception.message.lower()

    def test_execute_allows_same_brickset_different_users(self) -> None:
        """execute() allows multiple users to value same BrickSet."""
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        command1 = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=400,
        )
        self.service.execute(command1, self.user)

        command2 = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=500,
        )
        result = self.service.execute(command2, user2)

        assert result.user_id == user2.id
        assert Valuation.valuations.filter(user=self.user, brickset=self.brickset).exists()
        assert Valuation.valuations.filter(user=user2, brickset=self.brickset).exists()

    def test_execute_allows_same_user_different_bricksets(self) -> None:
        """execute() allows same user to value different BrickSets."""
        brickset2 = BrickSet.objects.create(
            owner=self.owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        command1 = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=400,
        )
        self.service.execute(command1, self.user)

        command2 = CreateValuationCommand(
            brickset_id=brickset2.id,
            value=200,
        )
        result = self.service.execute(command2, self.user)

        assert result.brickset_id == brickset2.id
        assert result.user_id == self.user.id
        assert Valuation.valuations.filter(user=self.user).count() == 2

    def test_execute_initializes_likes_count_to_zero(self) -> None:
        """execute() initializes likes_count to 0 in DTO."""
        command = CreateValuationCommand(
            brickset_id=self.brickset.id,
            value=300,
        )

        result = self.service.execute(command, self.user)

        assert result.likes_count == 0
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.likes_count == 0
