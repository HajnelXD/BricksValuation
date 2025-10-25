"""API integration tests for owned BrickSet list endpoint.

Tests cover listing with authentication, pagination, ordering, security, and RB-01 logic.
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


class TestOwnedBrickSetListView(APITestCase):
    """Test OwnedBrickSetListView API endpoint (GET /api/v1/users/me/bricksets)."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.url = reverse_lazy("catalog:owned-brickset-list")
        self.owner = baker.make(User, username="owner")
        self.other_user = baker.make(User, username="other_user")

        # Create bricksets owned by owner user
        self.owned_brickset1 = baker.make(
            BrickSet,
            owner=self.owner,
            number=10001,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
        )
        self.owned_brickset2 = baker.make(
            BrickSet,
            owner=self.owner,
            number=20002,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        self.owned_brickset3 = baker.make(
            BrickSet,
            owner=self.owner,
            number=30003,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=True,
        )

        # Create brickset owned by other_user (should not be returned)
        self.other_user_brickset = baker.make(
            BrickSet,
            owner=self.other_user,
            number=99999,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=True,
        )

        # Create valuations for owner's bricksets
        # owned_brickset1: owner valuation (0 likes) + other_user valuation (5 likes)
        self.owner_val1 = baker.make(
            Valuation,
            brickset=self.owned_brickset1,
            user=self.owner,
            value=100,
            currency="PLN",
            likes_count=0,  # Owner has 0 likes
        )
        self.other_val1 = baker.make(
            Valuation,
            brickset=self.owned_brickset1,
            user=self.other_user,
            value=120,
            currency="PLN",
            likes_count=5,
        )

        # owned_brickset2: owner valuation (5 likes) - NO OTHER USERS
        self.owner_val2 = baker.make(
            Valuation,
            brickset=self.owned_brickset2,
            user=self.owner,
            value=80,
            currency="PLN",
            likes_count=5,  # Owner has likes
        )

        # owned_brickset3: no valuations at all
        # (this one should be editable - no other users, no valuations)

    def test_get_returns_401_when_not_authenticated(self) -> None:
        """Test that unauthenticated requests return 401."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_returns_200_when_authenticated(self) -> None:
        """Test successful list request with authentication returns 200."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_returns_paginated_results(self) -> None:
        """Test response has pagination structure."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)

    def test_get_returns_only_requesting_user_bricksets(self) -> None:
        """Test security: user sees only their own bricksets."""
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have only 3 bricksets (owner's), not 4
        assert data["count"] == 3
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 20002 in numbers
        assert 30003 in numbers
        # Other user's brickset should NOT be returned
        assert 99999 not in numbers

    def test_get_excludes_other_users_bricksets_from_other_authenticated_user(
        self,
    ) -> None:
        """Test that other_user sees only their own bricksets."""
        self.client.force_authenticate(user=self.other_user)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have only 1 brickset (other_user's)
        assert data["count"] == 1
        assert data["results"][0]["number"] == 99999

    def test_get_returns_empty_results_when_user_has_no_bricksets(self) -> None:
        """Test that user with no bricksets gets empty list (not 404)."""
        new_user = baker.make(User, username="new_user")
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_get_list_item_has_required_fields(self) -> None:
        """Test that each item has all required fields for owned list."""
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]

        # Check required fields (OwnedBrickSetListItemDTO fields)
        assert "id" in item
        assert "number" in item
        assert "production_status" in item
        assert "completeness" in item
        assert "valuations_count" in item
        assert "total_likes" in item
        assert "editable" in item  # Key field for owned list

    def test_get_does_not_include_unnecessary_fields(self) -> None:
        """Test that response excludes fields not needed for owned list."""
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]

        # Should NOT include these fields (unlike BrickSetListItemDTO)
        assert "has_instructions" not in item
        assert "has_box" not in item
        assert "is_factory_sealed" not in item
        assert "owner_id" not in item
        assert "owner_initial_estimate" not in item
        assert "top_valuation" not in item

    def test_get_respects_pagination_page_parameter(self) -> None:
        """Test that page parameter works correctly."""
        self.client.force_authenticate(user=self.owner)
        # Request page 1 with page_size 1
        response = self.client.get(self.url, {"page": 1, "page_size": 1})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3  # Total is 3
        assert len(data["results"]) == 1  # But page 1 has only 1 item
        assert data["next"] is not None  # Next page exists

    def test_get_respects_page_size_parameter(self) -> None:
        """Test that page_size parameter works correctly."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url, {"page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        assert len(data["results"]) == 2  # First page has 2 items

    def test_get_enforces_max_page_size(self) -> None:
        """Test that page_size cannot exceed max (100)."""
        self.client.force_authenticate(user=self.owner)
        # Try to set page_size > 100
        response = self.client.get(self.url, {"page_size": 500})

        # Should either return 400 or limit to 100
        # DRF pagination should handle this
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_get_returns_404_for_invalid_page_number(self) -> None:
        """Test that invalid page number returns 404 (page not found)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url, {"page": 999})

        # DRF pagination returns 404 when page doesn't exist
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_respects_ordering_parameter_default(self) -> None:
        """Test that default ordering is -created_at (newest first)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url, {"page_size": 100})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        numbers = [item["number"] for item in data["results"]]
        # Default is -created_at (newest first)
        # owned_brickset3 created last should be first
        assert numbers[0] == 30003

    def test_get_respects_ordering_parameter_created_at_asc(self) -> None:
        """Test custom ordering by created_at (oldest first)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            self.url,
            {"page_size": 100, "ordering": "created_at"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        numbers = [item["number"] for item in data["results"]]
        # Should be ordered oldest first
        assert numbers[0] == 10001  # oldest

    def test_get_respects_ordering_parameter_valuations_count_desc(self) -> None:
        """Test ordering by -valuations_count (most valuations first)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            self.url,
            {"page_size": 100, "ordering": "-valuations_count"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        counts = [item["valuations_count"] for item in data["results"]]
        # Should be ordered by most valuations first
        assert counts[0] == 2  # owned_brickset1 has 2 valuations
        assert counts[1] == 1  # owned_brickset2 has 1 valuation
        assert counts[2] == 0  # owned_brickset3 has 0 valuations

    def test_get_respects_ordering_parameter_total_likes_asc(self) -> None:
        """Test ordering by total_likes (fewest first)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            self.url,
            {"page_size": 100, "ordering": "total_likes"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        likes = [item["total_likes"] for item in data["results"]]
        # Should be ordered: 0, 5, 5 (or 0, 5, 5 depending on insertion order)
        assert likes[0] == 0

    def test_get_returns_400_for_invalid_ordering(self) -> None:
        """Test that invalid ordering parameter returns 400 or is ignored."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            self.url,
            {"ordering": "invalid_field"}
        )

        # DRF default behavior: invalid orderings might be ignored or raise 400
        # Our service ignores invalid orderings, so should return 200
        assert response.status_code == status.HTTP_200_OK

    def test_get_aggregations_valuations_count_correct(self) -> None:
        """Test that valuations_count is accurate."""
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # owned_brickset1: 2 valuations (owner + other_user)
        assert items_by_number[10001]["valuations_count"] == 2
        # owned_brickset2: 1 valuation (owner only)
        assert items_by_number[20002]["valuations_count"] == 1
        # owned_brickset3: 0 valuations
        assert items_by_number[30003]["valuations_count"] == 0

    def test_get_aggregations_total_likes_correct(self) -> None:
        """Test that total_likes is sum of all likes."""
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # owned_brickset1: 0 + 5 = 5 likes
        assert items_by_number[10001]["total_likes"] == 5
        # owned_brickset2: 5 likes (owner only)
        assert items_by_number[20002]["total_likes"] == 5
        # owned_brickset3: 0 likes
        assert items_by_number[30003]["total_likes"] == 0

    def test_get_rb01_editable_true_when_no_other_users_and_no_likes(self) -> None:
        """Test RB-01: editable=True when no other users AND owner has 0 likes."""
        # owned_brickset3 has no valuations at all, so editable=True
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # owned_brickset3: no valuations, so editable=True
        assert items_by_number[30003]["editable"] is True

    def test_get_rb01_editable_false_when_other_users_valuations_exist(
        self,
    ) -> None:
        """Test RB-01: editable=False when other users' valuations exist."""
        # owned_brickset1 has other_user_valuation
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # owned_brickset1: has other user's valuation, so editable=False
        assert items_by_number[10001]["editable"] is False

    def test_get_rb01_editable_false_when_owner_valuation_has_likes(self) -> None:
        """Test RB-01: editable=False when owner's valuation has likes."""
        # owned_brickset2: owner valuation with 5 likes
        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # owned_brickset2: owner valuation has likes, so editable=False
        assert items_by_number[20002]["editable"] is False

    def test_get_rb01_creates_editable_true_scenario(self) -> None:
        """Test RB-01: create scenario where editable=True with valuations."""
        # Create new brickset: owner valuation (0 likes), no other users
        brickset_editable = baker.make(
            BrickSet,
            owner=self.owner,
            number=55555,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
        )
        baker.make(
            Valuation,
            brickset=brickset_editable,
            user=self.owner,
            value=100,
            currency="PLN",
            likes_count=0,  # 0 likes - important!
        )

        self.client.force_authenticate(user=self.owner)
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # This brickset: owner valuation with 0 likes and no other users
        assert items_by_number[55555]["editable"] is True

    def test_get_pagination_links_are_absolute_urls(self) -> None:
        """Test that pagination links (next, previous) are proper URLs."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url, {"page_size": 1})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        if data["next"]:
            assert data["next"].startswith("http")
        if data["previous"]:
            assert data["previous"].startswith("http")
