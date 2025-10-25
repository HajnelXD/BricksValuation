"""API integration tests for Valuation creation endpoint."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import BrickSet, Completeness, ProductionStatus
from valuation.models import Valuation

User = get_user_model()


class TestCreateValuationView(APITestCase):
    """Test BrickSetValuationsView POST /api/v1/bricksets/{id}/valuations endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user = baker.make(User)
        self.owner = baker.make(User)
        self.brickset = BrickSet.objects.create(
            owner=self.owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.url = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": self.brickset.id},
        )

    def test_post_successfully_creates_valuation_returns_created_status(self) -> None:
        """POST with valid payload creates Valuation and returns 201."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 450,
            "currency": "PLN",
            "comment": "Looks complete and in great condition",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Valuation.valuations.filter(user=self.user, brickset=self.brickset).exists()

    def test_post_response_status_code_is_created(self) -> None:
        """POST response status code is 201 Created."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 350,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_post_creates_valuation_without_optional_fields(self) -> None:
        """POST without optional currency and comment creates Valuation."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 250,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.currency == "PLN"  # default
        assert valuation.comment is None

    def test_post_sets_user_to_authenticated_user(self) -> None:
        """POST sets user to authenticated user."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 400,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user_id"] == self.user.id
        valuation = Valuation.valuations.get(user=self.user, brickset=self.brickset)
        assert valuation.user == self.user

    def test_post_response_includes_all_dto_fields(self) -> None:
        """POST response includes all ValuationDTO fields."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 500,
            "currency": "USD",
            "comment": "Excellent condition",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert "id" in data
        assert "brickset_id" in data
        assert "user_id" in data
        assert "value" in data
        assert "currency" in data
        assert "comment" in data
        assert "likes_count" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_post_response_contains_correct_values(self) -> None:
        """POST response contains correct values from request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 450,
            "currency": "EUR",
            "comment": "Good shape",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 450
        assert response.data["currency"] == "EUR"
        assert response.data["comment"] == "Good shape"
        assert response.data["brickset_id"] == self.brickset.id

    def test_post_persists_valuation_to_database(self) -> None:
        """POST persists Valuation to database."""
        self.client.force_authenticate(user=self.user)
        initial_count = Valuation.valuations.count()
        payload = {
            "value": 300,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Valuation.valuations.count() == initial_count + 1

    def test_post_validation_error_invalid_value_returns_bad_request(self) -> None:
        """POST with invalid value returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 1000000,  # exceeds maximum
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in response.data

    def test_post_validation_error_value_zero_returns_bad_request(self) -> None:
        """POST with value=0 returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 0,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in response.data

    def test_post_validation_error_missing_required_field(self) -> None:
        """POST missing required field returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "currency": "PLN",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in response.data

    def test_post_validation_error_invalid_currency_length_returns_bad_request(
        self,
    ) -> None:
        """POST with currency exceeding 3 chars returns 400."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 300,
            "currency": "TOOLONG",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "currency" in response.data

    def test_post_duplicate_valuation_returns_conflict(self) -> None:
        """POST duplicate valuation for same user-brickset returns 409 Conflict."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 400,
        }

        # Create first valuation
        response1 = self.client.post(self.url, payload, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate
        response2 = self.client.post(self.url, payload, format="json")
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "detail" in response2.data
        assert "constraint" in response2.data
        assert "already exists" in response2.data["detail"].lower()

    def test_post_nonexistent_brickset_returns_not_found(self) -> None:
        """POST to non-existent BrickSet returns 404 Not Found."""
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": 99999},
        )
        payload = {
            "value": 300,
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.data
        assert "not found" in response.data["detail"].lower()

    def test_post_requires_authentication_returns_unauthorized_without_jwt(self) -> None:
        """POST without authentication returns 401 Unauthorized."""
        payload = {
            "value": 300,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_response_content_type_is_json(self) -> None:
        """POST response Content-Type is application/json."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 300,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "application/json" in response.get("Content-Type", "")

    def test_post_response_has_correct_structure(self) -> None:
        """POST response has correct JSON structure."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 350,
            "currency": "GBP",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert isinstance(data, dict)
        assert data["value"] == 350
        assert data["currency"] == "GBP"

    def test_post_allows_multiple_users_same_brickset(self) -> None:
        """POST allows different users to create valuations for same BrickSet."""
        user2 = baker.make(User)

        # First user creates valuation
        self.client.force_authenticate(user=self.user)
        payload1 = {"value": 400}
        response1 = self.client.post(self.url, payload1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Second user creates valuation for same BrickSet
        self.client.force_authenticate(user=user2)
        payload2 = {"value": 450}
        response2 = self.client.post(self.url, payload2, format="json")
        assert response2.status_code == status.HTTP_201_CREATED

        # Both valuations exist
        assert Valuation.valuations.filter(user=self.user, brickset=self.brickset).exists()
        assert Valuation.valuations.filter(user=user2, brickset=self.brickset).exists()

    def test_post_allows_same_user_multiple_bricksets(self) -> None:
        """POST allows same user to create valuations for different BrickSets."""
        brickset2 = BrickSet.objects.create(
            owner=self.owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        url2 = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": brickset2.id},
        )

        self.client.force_authenticate(user=self.user)

        # First valuation
        response1 = self.client.post(self.url, {"value": 300}, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Second valuation for different BrickSet
        response2 = self.client.post(url2, {"value": 200}, format="json")
        assert response2.status_code == status.HTTP_201_CREATED

        # Both valuations exist
        assert Valuation.valuations.filter(user=self.user).count() == 2

    def test_post_response_likes_count_initialized_to_zero(self) -> None:
        """POST response has likes_count initialized to 0."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "value": 300,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["likes_count"] == 0
