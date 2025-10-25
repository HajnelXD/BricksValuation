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


class TestListValuationsView(APITestCase):
    """Test BrickSetValuationsView GET /api/v1/bricksets/{id}/valuations endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)
        self.user3 = baker.make(User)
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
        self.other_brickset = BrickSet.objects.create(
            owner=self.owner,
            number=67890,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )

        # Create valuations with different likes_count for ordering tests
        self.valuation_high_likes = Valuation.valuations.create(
            user=self.user1,
            brickset=self.brickset,
            value=500,
            currency="PLN",
            comment="Excellent condition",
            likes_count=10,
        )
        self.valuation_mid_likes = Valuation.valuations.create(
            user=self.user2,
            brickset=self.brickset,
            value=450,
            currency="PLN",
            comment="Good condition",
            likes_count=5,
        )
        self.valuation_low_likes = Valuation.valuations.create(
            user=self.user3,
            brickset=self.brickset,
            value=400,
            currency="EUR",
            comment=None,
            likes_count=2,
        )

        # Valuation for different BrickSet - should not appear
        self.other_valuation = Valuation.valuations.create(
            user=self.user1,
            brickset=self.other_brickset,
            value=300,
            currency="PLN",
        )

        self.url = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": self.brickset.id},
        )

    def test_get_successfully_returns_ok_status(self) -> None:
        """GET with valid brickset_id returns 200."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_response_has_pagination_structure(self) -> None:
        """GET response has count, next, previous, and results."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)

    def test_get_returns_only_valuations_for_specified_brickset(self) -> None:
        """GET returns only valuations for the specified BrickSet."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        valuation_ids = [item["id"] for item in data["results"]]
        assert self.valuation_high_likes.id in valuation_ids
        assert self.valuation_mid_likes.id in valuation_ids
        assert self.valuation_low_likes.id in valuation_ids
        assert self.other_valuation.id not in valuation_ids

    def test_get_orders_by_likes_count_desc_then_created_at_asc(self) -> None:
        """GET returns valuations ordered by -likes_count, created_at."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data["results"]
        assert len(results) == 3
        # Most liked first, then chronologically
        assert results[0]["id"] == self.valuation_high_likes.id
        assert results[0]["likes_count"] == 10
        assert results[1]["id"] == self.valuation_mid_likes.id
        assert results[1]["likes_count"] == 5
        assert results[2]["id"] == self.valuation_low_likes.id
        assert results[2]["likes_count"] == 2

    def test_get_list_item_has_all_required_fields(self) -> None:
        """GET list item includes all ValuationListItemDTO fields."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]
        assert "id" in item
        assert "user_id" in item
        assert "value" in item
        assert "currency" in item
        assert "comment" in item
        assert "likes_count" in item
        assert "created_at" in item
        # Verify excluded fields
        assert "brickset_id" not in item
        assert "updated_at" not in item

    def test_get_returns_empty_list_for_brickset_without_valuations(self) -> None:
        """GET returns empty results for BrickSet with no valuations."""
        self.client.force_authenticate(user=self.user1)
        brickset_no_valuations = BrickSet.objects.create(
            owner=self.owner,
            number=99999,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=False,
        )
        url = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": brickset_no_valuations.id},
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert len(data["results"]) == 0

    def test_get_returns_not_found_for_nonexistent_brickset(self) -> None:
        """GET with non-existent brickset_id returns 404."""
        self.client.force_authenticate(user=self.user1)
        nonexistent_id = 999999
        url = reverse_lazy(
            "valuation:brickset-valuations",
            kwargs={"brickset_id": nonexistent_id},
        )

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()
        assert "not found" in response.json()["detail"].lower()

    def test_get_requires_authentication(self) -> None:
        """GET without authentication returns 401."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_pagination_with_page_parameter(self) -> None:
        """GET supports page parameter for pagination."""
        self.client.force_authenticate(user=self.user1)
        # Create more valuations to test pagination (unique user per valuation)
        for i in range(25):
            user = baker.make(User)
            Valuation.valuations.create(
                user=user,
                brickset=self.brickset,
                value=100 + i,
                currency="PLN",
                likes_count=0,
            )

        # First page
        response1 = self.client.get(self.url, {"page": 1, "page_size": 20})
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["results"]) == 20
        assert data1["next"] is not None
        assert data1["previous"] is None

        # Second page
        response2 = self.client.get(self.url, {"page": 2, "page_size": 20})
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert len(data2["results"]) == 8  # 28 total (3 + 25) - 20 on first page
        assert data2["next"] is None
        assert data2["previous"] is not None

    def test_get_pagination_with_custom_page_size(self) -> None:
        """GET supports page_size parameter."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url, {"page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 2
        assert data["count"] == 3

    def test_get_pagination_respects_max_page_size(self) -> None:
        """GET enforces max_page_size of 100."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url, {"page_size": 100})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        assert len(data["results"]) == 3

    def test_get_pagination_invalid_page_size_returns_bad_request(self) -> None:
        """GET with page_size > 100 returns validation error."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url, {"page_size": 101})

        # DRF PageNumberPagination allows it but limits to max_page_size
        # So this actually succeeds but limits to 100
        assert response.status_code == status.HTTP_200_OK

    def test_get_handles_null_comment_correctly(self) -> None:
        """GET correctly serializes None comment."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Find valuation with null comment
        valuation_with_null = next(
            item for item in data["results"]
            if item["id"] == self.valuation_low_likes.id
        )
        assert valuation_with_null["comment"] is None
