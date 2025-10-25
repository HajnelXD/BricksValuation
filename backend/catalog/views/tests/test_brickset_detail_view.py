"""API integration tests for BrickSet detail endpoint.

Tests cover single object retrieval, valuations, aggregates, errors, and permissions.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import BrickSet, ProductionStatus, Completeness
from valuation.models import Valuation

User = get_user_model()


class TestBrickSetDetailView(APITestCase):
    """Test BrickSetDetailView API endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.user3 = baker.make(User)

        # Create brickset without valuations
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

        # Create brickset with valuations
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
            brickset=self.brickset_with_vals,
            user=self.user2,
            value=450,
            currency="PLN",
            comment="Excellent condition",
            likes_count=15,
        )
        self.valuation2 = baker.make(
            Valuation,
            brickset=self.brickset_with_vals,
            user=self.user3,
            value=420,
            currency="PLN",
            comment=None,
            likes_count=8,
        )

    def _get_detail_url(self, brickset_id: int) -> str:
        """Build URL for detail endpoint."""
        return reverse_lazy("catalog:brickset-detail", args=[brickset_id])

    def test_get_existing_brickset_returns_ok(self) -> None:
        """Test successful GET returns 200 OK."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_response_has_json_content_type(self) -> None:
        """Test response has application/json content type."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)

        assert response["Content-Type"] == "application/json"

    def test_get_response_includes_all_brickset_fields(self) -> None:
        """Test response includes all required brickset fields."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)
        data = response.json()

        # Check all brickset fields present
        required_fields = [
            "id",
            "number",
            "production_status",
            "completeness",
            "has_instructions",
            "has_box",
            "is_factory_sealed",
            "owner_initial_estimate",
            "owner_id",
            "valuations",
            "valuations_count",
            "total_likes",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in data

    def test_get_response_structure_matches_dto(self) -> None:
        """Test response structure matches BrickSetDetailDTO."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)
        data = response.json()

        assert data["id"] == self.brickset_empty.id
        assert data["number"] == self.brickset_empty.number
        assert data["production_status"] == ProductionStatus.ACTIVE
        assert data["completeness"] == Completeness.COMPLETE
        assert data["has_instructions"] is True
        assert data["has_box"] is True
        assert data["is_factory_sealed"] is False
        assert data["owner_initial_estimate"] == 250
        assert data["owner_id"] == self.user1.id

    def test_get_brickset_without_valuations(self) -> None:
        """Test GET returns empty valuations array for brickset without valuations."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)
        data = response.json()

        assert data["valuations"] == []
        assert data["valuations_count"] == 0
        assert data["total_likes"] == 0

    def test_get_brickset_with_single_valuation(self) -> None:
        """Test GET returns brickset with one valuation."""
        brickset = baker.make(BrickSet, owner=self.user1, number=50000)
        valuation = baker.make(
            Valuation,
            brickset=brickset,
            user=self.user2,
            value=300,
            currency="PLN",
            comment="Good",
            likes_count=5,
        )
        url = self._get_detail_url(brickset.id)

        response = self.client.get(url)
        data = response.json()

        assert len(data["valuations"]) == 1
        assert data["valuations"][0]["id"] == valuation.id
        assert data["valuations"][0]["value"] == 300
        assert data["valuations_count"] == 1
        assert data["total_likes"] == 5

    def test_get_brickset_with_multiple_valuations(self) -> None:
        """Test GET returns brickset with multiple valuations."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        assert len(data["valuations"]) == 2
        assert data["valuations"][0]["id"] == self.valuation1.id
        assert data["valuations"][1]["id"] == self.valuation2.id

    def test_get_valuations_count_matches_actual_count(self) -> None:
        """Test valuations_count matches actual valuations array length."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        assert data["valuations_count"] == len(data["valuations"])
        assert data["valuations_count"] == 2

    def test_get_total_likes_matches_sum(self) -> None:
        """Test total_likes is sum of all valuation likes."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        expected_total_likes = self.valuation1.likes_count + self.valuation2.likes_count
        assert data["total_likes"] == expected_total_likes
        assert data["total_likes"] == 23

    def test_get_response_includes_all_valuation_fields(self) -> None:
        """Test valuation objects include all required fields."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        valuation = data["valuations"][0]
        valuation_fields = [
            "id",
            "user_id",
            "value",
            "currency",
            "comment",
            "likes_count",
            "created_at",
        ]
        for field in valuation_fields:
            assert field in valuation

    def test_get_valuation_fields_match_model(self) -> None:
        """Test valuation DTO fields match model data."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        first_val = data["valuations"][0]
        assert first_val["id"] == self.valuation1.id
        assert first_val["user_id"] == self.user2.id
        assert first_val["value"] == 450
        assert first_val["currency"] == "PLN"
        assert first_val["comment"] == "Excellent condition"
        assert first_val["likes_count"] == 15

    def test_get_valuation_handles_null_comment(self) -> None:
        """Test valuation with null comment serializes correctly."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        second_val = data["valuations"][1]
        assert second_val["comment"] is None

    def test_get_nonexistent_brickset_returns_not_found(self) -> None:
        """Test GET nonexistent brickset returns 404."""
        url = self._get_detail_url(999999)

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_not_found_response_has_detail_message(self) -> None:
        """Test 404 response includes detail error message."""
        nonexistent_id = 777777
        url = self._get_detail_url(nonexistent_id)

        response = self.client.get(url)
        data = response.json()

        assert "detail" in data
        assert str(nonexistent_id) in data["detail"]

    def test_get_allows_unauthenticated_access(self) -> None:
        """Test endpoint allows unauthenticated users (AllowAny permission)."""
        url = self._get_detail_url(self.brickset_empty.id)

        # Ensure user is not authenticated
        self.client.force_authenticate(user=None)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_works_for_authenticated_user(self) -> None:
        """Test endpoint works for authenticated users."""
        url = self._get_detail_url(self.brickset_empty.id)

        # Authenticate as user
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_with_null_owner_initial_estimate(self) -> None:
        """Test response correctly handles null owner_initial_estimate."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        assert data["owner_initial_estimate"] is None

    def test_get_response_datetime_format_iso8601(self) -> None:
        """Test datetime fields are ISO8601 formatted."""
        url = self._get_detail_url(self.brickset_empty.id)

        response = self.client.get(url)
        data = response.json()

        # Both should be ISO8601 strings
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert "T" in data["created_at"]  # ISO format marker
        assert "T" in data["updated_at"]

    def test_get_valuations_datetime_format_iso8601(self) -> None:
        """Test valuation datetime fields are ISO8601 formatted."""
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        for valuation in data["valuations"]:
            assert isinstance(valuation["created_at"], str)
            assert "T" in valuation["created_at"]

    def test_get_three_valuations_aggregates_correct(self) -> None:
        """Test aggregates with three valuations."""
        # Add third valuation to existing brickset
        baker.make(
            Valuation,
            brickset=self.brickset_with_vals,
            user=self.user1,
            value=480,
            currency="PLN",
            comment="Rare find!",
            likes_count=22,
        )
        url = self._get_detail_url(self.brickset_with_vals.id)

        response = self.client.get(url)
        data = response.json()

        assert data["valuations_count"] == 3
        assert data["total_likes"] == 45  # 15 + 8 + 22
        assert len(data["valuations"]) == 3
