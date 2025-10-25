"""Tests for ValuationDetailView API endpoint."""
from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from account.models import User
from catalog.models import BrickSet
from valuation.models import Valuation


class ValuationDetailViewTests(APITestCase):
    """Test cases for GET /valuations/{id} detail endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test user and authenticate
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

        self.client.force_authenticate(user=self.user)

    def test_get_valuation_detail_success_returns_200(self) -> None:
        """Test successful GET returns 200 OK with complete valuation data."""
        url = reverse("valuation:valuation-detail", kwargs={"pk": self.valuation.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == self.valuation.id
        assert data["brickset_id"] == self.brickset.id
        assert data["user_id"] == self.user.id
        assert data["value"] == 500
        assert data["currency"] == "PLN"
        assert data["comment"] == "Great condition"
        assert data["likes_count"] == 5

    def test_get_valuation_includes_timestamps(self) -> None:
        """Test that GET response includes created_at and updated_at."""
        url = reverse("valuation:valuation-detail", kwargs={"pk": self.valuation.id})
        response = self.client.get(url)

        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_get_valuation_with_null_comment_returns_null(self) -> None:
        """Test that valuation with null comment returns null in response."""
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

        url = reverse(
            "valuation:valuation-detail",
            kwargs={"pk": valuation_no_comment.id},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] is None

    def test_get_nonexistent_valuation_returns_404(self) -> None:
        """Test that GET non-existent valuation returns 404 Not Found."""
        url = reverse("valuation:valuation-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "99999" in data["detail"]

    def test_get_unauthenticated_returns_401(self) -> None:
        """Test that unauthenticated request returns 401 Unauthorized."""
        self.client.force_authenticate(user=None)

        url = reverse("valuation:valuation-detail", kwargs={"pk": self.valuation.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_valuation_response_has_all_required_fields(self) -> None:
        """Test that response includes all 9 required fields."""
        url = reverse("valuation:valuation-detail", kwargs={"pk": self.valuation.id})
        response = self.client.get(url)

        data = response.json()
        required_fields = [
            "id",
            "brickset_id",
            "user_id",
            "value",
            "currency",
            "comment",
            "likes_count",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_get_multiple_different_valuations(self) -> None:
        """Test fetching different valuations returns correct data for each."""
        # Create second valuation
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

        # Get first valuation
        url1 = reverse(
            "valuation:valuation-detail",
            kwargs={"pk": self.valuation.id},
        )
        response1 = self.client.get(url1)
        data1 = response1.json()

        # Get second valuation
        url2 = reverse(
            "valuation:valuation-detail",
            kwargs={"pk": valuation2.id},
        )
        response2 = self.client.get(url2)
        data2 = response2.json()

        # Verify they are different
        assert data1["id"] == self.valuation.id
        assert data2["id"] == valuation2.id
        assert data1["value"] == 500
        assert data2["value"] == 1000
        assert data1["currency"] == "PLN"
        assert data2["currency"] == "EUR"

    def test_get_valuation_returns_specific_user_valuation(self) -> None:
        """Test that endpoint returns valuation by any user (public read)."""
        # Create second user
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="pass123",
        )

        # Create valuation by other user for same brickset
        brickset3 = BrickSet.objects.create(
            number=70622,
            production_status="RETIRED",
            completeness="COMPLETE",
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner=self.user,
        )

        other_valuation = Valuation.valuations.create(
            user=other_user,
            brickset=brickset3,
            value=750,
            currency="GBP",
            comment="Other user valuation",
            likes_count=3,
        )

        # Current user fetches other user's valuation
        url = reverse(
            "valuation:valuation-detail",
            kwargs={"pk": other_valuation.id},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == other_user.id
        assert data["value"] == 750

    def test_get_valuation_not_found_message_format(self) -> None:
        """Test that 404 error message has correct format."""
        url = reverse("valuation:valuation-detail", kwargs={"pk": 12345})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Valuation with id 12345 not found."
