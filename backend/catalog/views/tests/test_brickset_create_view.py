"""API integration tests for BrickSet creation endpoint."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import BrickSet

User = get_user_model()


class TestCreateBrickSetView(APITestCase):
    """Test CreateBrickSetView POST /api/v1/bricksets endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.url = reverse_lazy("catalog:brickset-list")  # POST + GET same endpoint
        self.user = baker.make(User)

    def test_post_successfully_creates_brickset_returns_created_status(self) -> None:
        """POST with valid payload creates BrickSet and returns 201."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 360,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_with_valid_jwt_creates_brickset(self) -> None:
        """POST with valid auth and payload creates BrickSet."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 360,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert BrickSet.objects.filter(number=12345).exists()

    def test_post_response_status_code_is_created(self) -> None:
        """POST response status code is 201 Created."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_post_creates_brickset_without_owner_initial_estimate(self) -> None:
        """POST without owner_initial_estimate creates BrickSet."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 67890,
            "production_status": "RETIRED",
            "completeness": "INCOMPLETE",
            "has_instructions": False,
            "has_box": False,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        brickset = BrickSet.objects.get(number=67890)
        assert brickset.owner_initial_estimate is None

    def test_post_sets_owner_to_authenticated_user(self) -> None:
        """POST sets owner to authenticated user."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 11111,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["owner_id"] == self.user.id
        brickset = BrickSet.objects.get(number=11111)
        assert brickset.owner == self.user

    def test_post_response_includes_all_dto_fields(self) -> None:
        """POST response includes all BrickSetListItemDTO fields."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 22222,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 500,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert "id" in data
        assert "number" in data
        assert "production_status" in data
        assert "completeness" in data
        assert "has_instructions" in data
        assert "has_box" in data
        assert "is_factory_sealed" in data
        assert "owner_id" in data
        assert "owner_initial_estimate" in data
        assert "valuations_count" in data
        assert "total_likes" in data
        assert "top_valuation" in data

    def test_post_persists_brickset_to_database(self) -> None:
        """POST persists BrickSet to database."""
        self.client.force_authenticate(user=self.user)
        initial_count = BrickSet.objects.count()
        payload = {
            "number": 33333,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert BrickSet.objects.count() == initial_count + 1

    def test_post_validation_error_invalid_number_returns_bad_request(self) -> None:
        """POST with invalid number returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 10000000,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_validation_error_missing_required_field(self) -> None:
        """POST missing required field returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "number" in response.data

    def test_post_validation_error_invalid_production_status_returns_bad_request(
        self,
    ) -> None:
        """POST with invalid production_status returns 400."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "UNKNOWN",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "production_status" in response.data

    def test_post_validation_error_invalid_completeness_returns_bad_request(self) -> None:
        """POST with invalid completeness returns 400."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "MAYBE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "completeness" in response.data

    def test_post_validation_error_invalid_estimate_returns_bad_request(self) -> None:
        """POST with invalid owner_initial_estimate returns 400."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 0,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "owner_initial_estimate" in response.data

    def test_post_duplicate_brickset_returns_conflict(self) -> None:
        """POST duplicate BrickSet returns 409 Conflict."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        # Create first
        response1 = self.client.post(self.url, payload, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate
        response2 = self.client.post(self.url, payload, format="json")
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "detail" in response2.data
        assert "constraint" in response2.data

    def test_post_requires_authentication_returns_unauthorized_without_jwt(self) -> None:
        """POST without authentication returns 401 Unauthorized."""
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_response_content_type_is_json(self) -> None:
        """POST response Content-Type is application/json."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "application/json" in response.get("Content-Type", "")

    def test_post_response_has_correct_structure(self) -> None:
        """POST response has correct JSON structure."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 12345,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert isinstance(data, dict)
        assert data["number"] == 12345
        assert data["production_status"] == "ACTIVE"
        assert data["completeness"] == "COMPLETE"

    def test_post_new_brickset_visible_in_list_endpoint(self) -> None:
        """POST created BrickSet is visible in GET list endpoint."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 55555,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        list_url = reverse_lazy("catalog:brickset-list")
        list_response = self.client.get(list_url)

        assert list_response.status_code == status.HTTP_200_OK
        numbers = [item["number"] for item in list_response.data["results"]]
        assert 55555 in numbers

    def test_post_response_initial_aggregate_values(self) -> None:
        """POST response has correct initial aggregate values."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 44444,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert data["valuations_count"] == 0
        assert data["total_likes"] == 0
        assert data["top_valuation"] is None

    def test_post_returns_dto_with_all_fields(self) -> None:
        """POST returns complete DTO with all required fields."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "number": 99999,
            "production_status": "ACTIVE",
            "completeness": "COMPLETE",
            "has_instructions": True,
            "has_box": True,
            "is_factory_sealed": False,
            "owner_initial_estimate": 1000,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert data["id"] is not None
        assert data["number"] == 99999
        assert data["production_status"] == "ACTIVE"
        assert data["completeness"] == "COMPLETE"
        assert data["has_instructions"] is True
        assert data["has_box"] is True
        assert data["is_factory_sealed"] is False
        assert data["owner_initial_estimate"] == 1000
        assert data["owner_id"] == self.user.id
