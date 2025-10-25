"""Tests for ValuationDetailService."""
from __future__ import annotations

from django.test import TestCase

from catalog.models import BrickSet
from datastore.domains.valuation_dto import ValuationDetailDTO
from account.models import User
from valuation.exceptions import ValuationNotFoundError
from valuation.models import Valuation
from valuation.services.valuation_detail_service import ValuationDetailService


class ValuationDetailServiceTests(TestCase):
    """Test cases for ValuationDetailService.execute() method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = ValuationDetailService()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create test brickset
        self.brickset = BrickSet.objects.create(
            number=70620,
            production_status="RETIRED",
            completeness="COMPLETE",
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner=self.user,
        )

        # Create test valuation
        self.valuation = Valuation.valuations.create(
            user=self.user,
            brickset=self.brickset,
            value=500,
            currency="PLN",
            comment="Great condition",
            likes_count=5,
        )

    def test_execute_returns_valuation_detail_dto(self) -> None:
        """Test that execute returns ValuationDetailDTO with correct data."""
        result = self.service.execute(self.valuation.id)

        assert isinstance(result, ValuationDetailDTO)
        assert result.id == self.valuation.id
        assert result.brickset_id == self.brickset.id
        assert result.user_id == self.user.id
        assert result.value == 500
        assert result.currency == "PLN"
        assert result.comment == "Great condition"
        assert result.likes_count == 5

    def test_execute_includes_timestamps(self) -> None:
        """Test that execute includes created_at and updated_at in DTO."""
        result = self.service.execute(self.valuation.id)

        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.created_at == self.valuation.created_at
        assert result.updated_at == self.valuation.updated_at

    def test_execute_with_null_comment(self) -> None:
        """Test that execute handles null comment correctly."""
        # Create separate brickset for null comment valuation
        brickset_no_comment = BrickSet.objects.create(
            number=70621,
            production_status="CURRENT",
            completeness="INCOMPLETE",
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
            owner=self.user,
        )

        valuation_no_comment = Valuation.valuations.create(
            user=self.user,
            brickset=brickset_no_comment,
            value=300,
            currency="USD",
            comment=None,
            likes_count=0,
        )

        result = self.service.execute(valuation_no_comment.id)

        assert result.comment is None

    def test_execute_raises_not_found_for_missing_valuation(self) -> None:
        """Test that execute raises ValuationNotFoundError for non-existent id."""
        missing_id = 99999
        exception_raised = False
        raised_exception: ValuationNotFoundError | None = None

        try:
            self.service.execute(missing_id)
        except ValuationNotFoundError as exc:
            exception_raised = True
            raised_exception = exc

        assert exception_raised, "ValuationNotFoundError should be raised"
        assert raised_exception is not None
        assert raised_exception.valuation_id == missing_id
        assert str(missing_id) in raised_exception.message

    def test_execute_dto_mapping_all_fields(self) -> None:
        """Test that all valuation fields are correctly mapped to DTO."""
        result = self.service.execute(self.valuation.id)

        # Verify all required value fields present
        assert hasattr(result, "id")
        assert hasattr(result, "brickset_id")
        assert hasattr(result, "user_id")
        assert hasattr(result, "value")
        assert hasattr(result, "currency")
        assert hasattr(result, "comment")
        assert hasattr(result, "likes_count")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")

        # Verify DTO instance fields include all 9 value fields
        # (note: source_model ClassVar may also appear in __dataclass_fields__)
        value_fields = {
            "id",
            "brickset_id",
            "user_id",
            "value",
            "currency",
            "comment",
            "likes_count",
            "created_at",
            "updated_at",
        }
        actual_fields = set(result.__dataclass_fields__.keys())
        # All value_fields must be in actual_fields
        missing_fields = value_fields - actual_fields
        assert not missing_fields, f"Missing fields: {missing_fields}"

    def test_execute_multiple_valuations_different_ids(self) -> None:
        """Test that execute can fetch different valuations independently."""
        # Create second valuation for different brickset
        brickset2 = BrickSet.objects.create(
            number=70621,
            production_status="CURRENT",
            completeness="INCOMPLETE",
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
            owner=self.user,
        )

        valuation2 = Valuation.valuations.create(
            user=self.user,
            brickset=brickset2,
            value=1000,
            currency="EUR",
            comment="Different valuation",
            likes_count=10,
        )

        # Fetch both valuations
        result1 = self.service.execute(self.valuation.id)
        result2 = self.service.execute(valuation2.id)

        # Verify they are different
        assert result1.id != result2.id
        assert result1.brickset_id == self.brickset.id
        assert result2.brickset_id == brickset2.id
        assert result1.value == 500
        assert result2.value == 1000
