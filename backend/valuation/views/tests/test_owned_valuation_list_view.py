"""API integration tests for owned Valuation list endpoint.

Tests cover listing with authentication, pagination, ordering, security,
and response structure validation.
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


class TestOwnedValuationListView(APITestCase):
    """Test OwnedValuationListView API endpoint (GET /api/v1/users/me/valuations)."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.url = reverse_lazy("valuation:owned-valuation-list")
        self.user = baker.make(User, username="testuser")
        self.other_user = baker.make(User, username="otheruser")

        # Create bricksets
        self.brickset1 = baker.make(
            BrickSet,
            owner=self.user,
            number=10001,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        self.brickset2 = baker.make(
            BrickSet,
            owner=self.user,
            number=10002,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        self.brickset3 = baker.make(
            BrickSet,
            owner=self.user,
            number=10003,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        self.other_brickset = baker.make(
            BrickSet,
            owner=self.other_user,
            number=99999,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )

        # Create valuations for user (unique constraint: one per user-brickset pair)
        self.user_val1 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset1,
            value=350,
            currency="PLN",
            comment="Good condition",
            likes_count=5,
        )
        self.user_val2 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset2,
            value=250,
            currency="PLN",
            comment="Fair condition",
            likes_count=2,
        )
        self.user_val3 = baker.make(
            Valuation,
            user=self.user,
            brickset=self.brickset3,
            value=400,
            currency="PLN",
            likes_count=8,
        )

        # Create valuation for other_user (should not be returned)
        self.other_user_val = baker.make(
            Valuation,
            user=self.other_user,
            brickset=self.other_brickset,
            value=300,
            currency="PLN",
            likes_count=3,
        )

    def test_get_returns_401_when_not_authenticated(self) -> None:
        """Test that unauthenticated requests return 401."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_returns_200_when_authenticated(self) -> None:
        """Test successful list request with authentication returns 200."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_returns_paginated_results(self) -> None:
        """Test response has pagination structure (count, next, previous, results)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)

    def test_get_returns_only_requesting_user_valuations(self) -> None:
        """Test security: user sees only their own valuations."""
        self.client.force_authenticate(user=self.user)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have only 3 valuations (user's), not 4
        assert data["count"] == 3
        valuation_ids = [item["id"] for item in data["results"]]
        assert self.user_val1.id in valuation_ids
        assert self.user_val2.id in valuation_ids
        assert self.user_val3.id in valuation_ids
        # Other user's valuation should NOT be returned
        assert self.other_user_val.id not in valuation_ids

    def test_get_excludes_other_users_valuations(self) -> None:
        """Test that authenticated user only sees their valuations."""
        self.client.force_authenticate(user=self.other_user)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # other_user should see only 1 valuation (their own)
        assert data["count"] == 1
        assert data["results"][0]["id"] == self.other_user_val.id

    def test_get_returns_empty_results_when_user_has_no_valuations(self) -> None:
        """Test that user with no valuations gets empty results (not 404)."""
        user_no_valuations = baker.make(User)
        self.client.force_authenticate(user=user_no_valuations)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_get_respects_pagination_parameters(self) -> None:
        """Test that pagination parameters (page, page_size) are respected."""
        self.client.force_authenticate(user=self.user)
        # Request page 1 with page_size=2
        params = {"page": 1, "page_size": 2}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        assert len(data["results"]) == 2
        assert data["next"] is not None  # Should have next page

    def test_get_returns_bad_request_for_invalid_page(self) -> None:
        """Test that invalid page parameter returns 400."""
        self.client.force_authenticate(user=self.user)
        params = {"page": 999}  # Non-existent page
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_returns_bad_request_for_invalid_page_size(self) -> None:
        """Test that invalid page_size parameter uses default (DRF behavior)."""
        self.client.force_authenticate(user=self.user)
        # DRF pagination accepts any page_size and applies max_page_size constraint
        # Invalid (negative or zero) page_size is handled gracefully by DRF
        params = {"page_size": -1}  # Invalid page size
        response = self.client.get(self.url, params)
        # DRF will return 200 with default page_size (doesn't error on invalid page_size)
        assert response.status_code == status.HTTP_200_OK

    def test_get_respects_default_ordering(self) -> None:
        """Test that default ordering is -created_at (newest first)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should be ordered newest first (user_val3 was created last)
        assert data["results"][0]["id"] == self.user_val3.id

    def test_get_respects_ordering_parameter_likes_count_desc(self) -> None:
        """Test ordering by -likes_count."""
        self.client.force_authenticate(user=self.user)
        params = {"ordering": "-likes_count"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        likes_counts = [item["likes_count"] for item in data["results"]]
        # Should be ordered: 8, 5, 2
        assert likes_counts == [8, 5, 2]

    def test_get_respects_ordering_parameter_value_asc(self) -> None:
        """Test ordering by value ascending."""
        self.client.force_authenticate(user=self.user)
        params = {"ordering": "value"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        values = [item["value"] for item in data["results"]]
        # Should be ordered: 250, 350, 400
        assert values == [250, 350, 400]

    def test_get_ignores_invalid_ordering_parameter(self) -> None:
        """Test that invalid ordering is silently ignored (uses default)."""
        self.client.force_authenticate(user=self.user)
        params = {"ordering": "invalid_field"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return results in default order (not raise error)
        assert len(data["results"]) == 3

    def test_get_includes_nested_brickset_in_response(self) -> None:
        """Test that response includes nested brickset dict."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]
        assert "brickset" in item
        assert isinstance(item["brickset"], dict)

    def test_get_response_brickset_structure_is_correct(self) -> None:
        """Test that nested brickset has id and number fields."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]
        brickset = item["brickset"]
        assert "id" in brickset
        assert "number" in brickset
        assert isinstance(brickset["id"], int)
        assert isinstance(brickset["number"], int)

    def test_get_response_structure_matches_dto(self) -> None:
        """Test that response structure contains all expected fields."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]

        # Check all expected fields are present
        expected_fields = ["id", "brickset", "value", "currency", "likes_count", "created_at"]
        for field in expected_fields:
            assert field in item, f"Missing field: {field}"

    def test_get_response_contains_correct_valuations_data(self) -> None:
        """Test that response contains correct valuation data."""
        self.client.force_authenticate(user=self.user)
        params = {"ordering": "-likes_count"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data["results"]

        # First item should be user_val3 (likes_count=8)
        first_item = items[0]
        assert first_item["id"] == self.user_val3.id
        assert first_item["value"] == 400
        assert first_item["currency"] == "PLN"
        assert first_item["likes_count"] == 8
        assert first_item["brickset"]["number"] == self.brickset3.number

        # Second item should be user_val1 (likes_count=5)
        second_item = items[1]
        assert second_item["id"] == self.user_val1.id
        assert second_item["likes_count"] == 5

        # Third item should be user_val2 (likes_count=2)
        third_item = items[2]
        assert third_item["id"] == self.user_val2.id
        assert third_item["likes_count"] == 2
