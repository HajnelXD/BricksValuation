"""Tests for BrickSetDetailService."""
from __future__ import annotations

from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker

from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet, ProductionStatus, Completeness
from catalog.services.brickset_detail_service import BrickSetDetailService
from datastore.domains.catalog_dto import BrickSetDetailDTO, ValuationInlineDTO
from valuation.models import Valuation

User = get_user_model()


class BrickSetDetailServiceTests(TestCase):
    """Test suite for BrickSetDetailService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = BrickSetDetailService()
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.user3 = baker.make(User)

        # Create test brickset with no valuations
        self.brickset_empty = baker.make(
            BrickSet,
            owner=self.user1,
            number=10001,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=250,
        )

        # Create test brickset with valuations
        self.brickset_with_vals = baker.make(
            BrickSet,
            owner=self.user1,
            number=12345,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
            owner_initial_estimate=None,
        )

        # Create valuations for brickset_with_vals
        self.valuation1 = baker.make(
            Valuation,
            user=self.user2,
            brickset=self.brickset_with_vals,
            value=450,
            currency="PLN",
            comment="Excellent condition",
            likes_count=15,
        )
        self.valuation2 = baker.make(
            Valuation,
            user=self.user3,
            brickset=self.brickset_with_vals,
            value=420,
            currency="PLN",
            comment=None,
            likes_count=8,
        )

    def test_execute_returns_dto_for_existing_brickset(self) -> None:
        """Test execute returns BrickSetDetailDTO for valid id."""
        result = self.service.execute(self.brickset_empty.id)

        assert isinstance(result, BrickSetDetailDTO)
        assert result.id == self.brickset_empty.id

    def test_execute_returns_brickset_without_valuations(self) -> None:
        """Test execute returns brickset with no valuations."""
        result = self.service.execute(self.brickset_empty.id)

        assert result.valuations == []
        assert result.valuations_count == 0
        assert result.total_likes == 0

    def test_execute_returns_brickset_with_single_valuation(self) -> None:
        """Test execute returns brickset with one valuation."""
        # Create separate brickset with one valuation
        brickset = baker.make(BrickSet, owner=self.user1, number=50000)
        valuation = baker.make(
            Valuation,
            user=self.user2,
            brickset=brickset,
            value=300,
            currency="PLN",
            comment="Good",
            likes_count=5,
        )

        result = self.service.execute(brickset.id)

        assert len(result.valuations) == 1
        assert result.valuations[0].id == valuation.id
        assert result.valuations_count == 1
        assert result.total_likes == 5

    def test_execute_returns_brickset_with_multiple_valuations(self) -> None:
        """Test execute returns brickset with multiple valuations."""
        result = self.service.execute(self.brickset_with_vals.id)

        assert len(result.valuations) == 2
        assert result.valuations_count == 2

    def test_execute_aggregates_valuations_count_correctly(self) -> None:
        """Test valuations_count is calculated correctly."""
        result = self.service.execute(self.brickset_with_vals.id)

        assert result.valuations_count == 2

    def test_execute_aggregates_total_likes_correctly(self) -> None:
        """Test total_likes sums all valuation likes."""
        # valuation1 has 15 likes, valuation2 has 8 likes = 23 total
        result = self.service.execute(self.brickset_with_vals.id)

        assert result.total_likes == 23

    def test_execute_returns_dto_with_all_brickset_fields(self) -> None:
        """Test returned DTO has all brickset fields."""
        result = self.service.execute(self.brickset_with_vals.id)

        assert result.id == self.brickset_with_vals.id
        assert result.number == self.brickset_with_vals.number
        assert result.production_status == ProductionStatus.RETIRED
        assert result.completeness == Completeness.COMPLETE
        assert result.has_instructions is True
        assert result.has_box is False
        assert result.is_factory_sealed is False
        assert result.owner_initial_estimate is None
        assert result.owner_id == self.user1.id
        assert result.created_at == self.brickset_with_vals.created_at
        assert result.updated_at == self.brickset_with_vals.updated_at

    def test_execute_returns_valuations_in_creation_order(self) -> None:
        """Test valuations are returned in creation order (ascending)."""
        result = self.service.execute(self.brickset_with_vals.id)

        # Should be in order: valuation1, valuation2
        assert result.valuations[0].id == self.valuation1.id
        assert result.valuations[1].id == self.valuation2.id

    def test_execute_maps_valuation_fields_correctly(self) -> None:
        """Test valuation DTO fields are mapped correctly."""
        result = self.service.execute(self.brickset_with_vals.id)
        first_val_dto = result.valuations[0]

        assert first_val_dto.id == self.valuation1.id
        assert first_val_dto.user_id == self.user2.id
        assert first_val_dto.value == 450
        assert first_val_dto.currency == "PLN"
        assert first_val_dto.comment == "Excellent condition"
        assert first_val_dto.likes_count == 15
        assert first_val_dto.created_at == self.valuation1.created_at

    def test_execute_handles_null_valuation_comment(self) -> None:
        """Test valuation DTO handles null comment field."""
        result = self.service.execute(self.brickset_with_vals.id)
        second_val_dto = result.valuations[1]

        assert second_val_dto.comment is None

    def test_execute_with_null_owner_initial_estimate(self) -> None:
        """Test execute with null owner_initial_estimate."""
        result = self.service.execute(self.brickset_with_vals.id)

        assert result.owner_initial_estimate is None

    def test_execute_raises_not_found_for_nonexistent_id(self) -> None:
        """Test execute raises BrickSetNotFoundError for invalid id."""
        with self.assertRaises(BrickSetNotFoundError):
            self.service.execute(999999)

    def test_execute_not_found_error_includes_id_in_message(self) -> None:
        """Test BrickSetNotFoundError message includes the brickset id."""
        nonexistent_id = 777777

        with self.assertRaises(BrickSetNotFoundError) as error_context:
            self.service.execute(nonexistent_id)

        # Validate error attributes inside assertRaises context
        raised_error = error_context.exception  # noqa: WPS441
        assert raised_error.brickset_id == nonexistent_id
        assert str(nonexistent_id) in str(raised_error)

    def test_execute_returns_correct_dto_type(self) -> None:
        """Test that execute always returns BrickSetDetailDTO."""
        result1 = self.service.execute(self.brickset_empty.id)
        result2 = self.service.execute(self.brickset_with_vals.id)

        assert isinstance(result1, BrickSetDetailDTO)
        assert isinstance(result2, BrickSetDetailDTO)

    def test_execute_valuations_are_dto_instances(self) -> None:
        """Test that valuations in result are ValuationInlineDTO instances."""
        result = self.service.execute(self.brickset_with_vals.id)

        for valuation_dto in result.valuations:
            assert isinstance(valuation_dto, ValuationInlineDTO)

    def test_execute_with_three_valuations_aggregates(self) -> None:
        """Test aggregates with three valuations."""
        # Add third valuation
        baker.make(
            Valuation,
            user=self.user1,
            brickset=self.brickset_with_vals,
            value=480,
            currency="PLN",
            comment="Rare find!",
            likes_count=22,
        )

        result = self.service.execute(self.brickset_with_vals.id)

        # Should have all three valuations
        assert result.valuations_count == 3
        assert result.total_likes == 45  # 15 + 8 + 22
        assert len(result.valuations) == 3
