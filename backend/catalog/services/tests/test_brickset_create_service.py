"""Tests for CreateBrickSetService."""
from __future__ import annotations

from django.test import TestCase

from account.models import User
from catalog.exceptions import BrickSetDuplicateError
from catalog.models import BrickSet, Completeness, ProductionStatus
from catalog.services.brickset_create_service import CreateBrickSetService
from datastore.domains.catalog_dto import BrickSetListItemDTO, CreateBrickSetCommand


class CreateBrickSetServiceTests(TestCase):
    """Test CreateBrickSetService.execute() flow and error handling."""

    def setUp(self) -> None:
        """Create test user."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = CreateBrickSetService()

    def test_execute_creates_brickset_with_all_fields(self) -> None:
        """execute() successfully creates BrickSet with all fields."""
        command = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=360,
        )

        result = self.service.execute(command, self.user)

        assert isinstance(result, BrickSetListItemDTO)
        assert result.number == 12345
        assert result.owner_initial_estimate == 360
        assert BrickSet.objects.filter(number=12345).exists()

    def test_execute_creates_brickset_without_estimate(self) -> None:
        """execute() creates BrickSet with owner_initial_estimate=None."""
        command = CreateBrickSetCommand(
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=None,
        )

        result = self.service.execute(command, self.user)

        assert result.owner_initial_estimate is None
        brickset = BrickSet.objects.get(number=67890)
        assert brickset.owner_initial_estimate is None

    def test_execute_sets_correct_owner(self) -> None:
        """execute() sets owner to provided user."""
        command = CreateBrickSetCommand(
            number=11111,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command, self.user)

        assert result.owner_id == self.user.id
        brickset = BrickSet.objects.get(number=11111)
        assert brickset.owner == self.user

    def test_execute_returns_brickset_list_item_dto(self) -> None:
        """execute() returns BrickSetListItemDTO."""
        command = CreateBrickSetCommand(
            number=22222,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command, self.user)

        assert isinstance(result, BrickSetListItemDTO)

    def test_execute_dto_has_initial_aggregate_values(self) -> None:
        """execute() returns DTO with initial aggregate values."""
        command = CreateBrickSetCommand(
            number=33333,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command, self.user)

        assert result.valuations_count == 0
        assert result.total_likes == 0
        assert result.top_valuation is None

    def test_execute_persists_brickset_to_database(self) -> None:
        """execute() persists BrickSet to database."""
        initial_count = BrickSet.objects.count()
        command = CreateBrickSetCommand(
            number=44444,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        self.service.execute(command, self.user)

        assert BrickSet.objects.count() == initial_count + 1

    def test_execute_raises_duplicate_error_for_identical_combination(self) -> None:
        """execute() raises BrickSetDuplicateError for duplicate constraint."""
        # Create first BrickSet
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        # Try to create identical second BrickSet
        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        with self.assertRaises(BrickSetDuplicateError) as context:
            self.service.execute(command2, self.user)

        assert context.exception.constraint == "brickset_global_identity"

    def test_execute_allows_same_number_different_production_status(self) -> None:
        """execute() allows same number with different production_status."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command2, self.user)
        assert result.number == 12345
        assert result.production_status == ProductionStatus.RETIRED

    def test_execute_allows_same_number_different_completeness(self) -> None:
        """execute() allows same number with different completeness."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.INCOMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command2, self.user)
        assert result.completeness == Completeness.INCOMPLETE

    def test_execute_allows_same_number_different_has_instructions(self) -> None:
        """execute() allows same number with different has_instructions."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=False,
            has_box=True,
            is_factory_sealed=False,
        )

        result = self.service.execute(command2, self.user)
        assert result.has_instructions is False

    def test_execute_allows_same_number_different_has_box(self) -> None:
        """execute() allows same number with different has_box."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
        )

        result = self.service.execute(command2, self.user)
        assert result.has_box is False

    def test_execute_allows_same_number_different_is_factory_sealed(self) -> None:
        """execute() allows same number with different is_factory_sealed."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=True,
        )

        result = self.service.execute(command2, self.user)
        assert result.is_factory_sealed is True

    def test_execute_transaction_rollback_on_integrity_error(self) -> None:
        """execute() rolls back transaction on IntegrityError."""
        initial_count = BrickSet.objects.count()

        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        with self.assertRaises(BrickSetDuplicateError):
            self.service.execute(command2, self.user)

        # Count should only increase by 1 (first insert), not 2
        assert BrickSet.objects.count() == initial_count + 1

    def test_execute_duplicate_error_includes_constraint_name(self) -> None:
        """execute() DuplicateError includes constraint name."""
        command1 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.service.execute(command1, self.user)

        command2 = CreateBrickSetCommand(
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )

        with self.assertRaises(BrickSetDuplicateError) as duplicate_error:
            self.service.execute(command2, self.user)

        assert duplicate_error.exception.constraint == "brickset_global_identity"
        assert duplicate_error.exception.message == "BrickSet with this combination already exists."
