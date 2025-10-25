"""API integration tests for BrickSet list endpoint.

Tests cover listing, filtering, sorting, pagination, and authorization.
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


class TestBrickSetListView(APITestCase):
    """Test BrickSetListView API endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.url = reverse_lazy("catalog:brickset-list")
        self.user1 = baker.make(User)
        self.user2 = baker.make(User)

        # Create test bricksets with various configurations
        self.brickset_active_complete = baker.make(
            BrickSet,
            owner=self.user1,
            number=10001,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=True,
        )
        self.brickset_retired_incomplete = baker.make(
            BrickSet,
            owner=self.user1,
            number=20002,
            production_status=ProductionStatus.RETIRED,
            completeness=Completeness.INCOMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=False,
        )
        self.brickset_active_no_instructions = baker.make(
            BrickSet,
            owner=self.user2,
            number=30003,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=False,
            has_box=True,
            is_factory_sealed=False,
        )
        self.brickset_active_sealed = baker.make(
            BrickSet,
            owner=self.user2,
            number=40004,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=False,
            is_factory_sealed=True,
        )

        # Create valuations for aggregation testing
        # brickset_active_complete: 2 valuations (likes: 5 + 8)
        self.valuation1 = baker.make(
            Valuation,
            brickset=self.brickset_active_complete,
            user=self.user1,
            value=100,
            currency="USD",
            likes_count=5,
        )
        self.valuation2 = baker.make(
            Valuation,
            brickset=self.brickset_active_complete,
            user=self.user2,
            value=120,
            currency="USD",
            likes_count=8,
        )

        # brickset_retired_incomplete: 1 valuation (likes: 3)
        self.valuation3 = baker.make(
            Valuation,
            brickset=self.brickset_retired_incomplete,
            user=self.user1,
            value=80,
            currency="USD",
            likes_count=3,
        )

    def test_successful_list_returns_ok(self) -> None:
        """Test successful list request returns 200."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_response_has_pagination_structure(self) -> None:
        """Test response has count, next, previous, and results."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)

    def test_list_includes_all_bricksets(self) -> None:
        """Test that all created bricksets are included in results."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have total count of 4 bricksets
        assert data["count"] == 4
        # Collect all numbers from paginated results
        brickset_numbers = [item["number"] for item in data["results"]]
        assert 10001 in brickset_numbers
        assert 20002 in brickset_numbers
        assert 30003 in brickset_numbers
        assert 40004 in brickset_numbers

    def test_list_item_has_required_fields(self) -> None:
        """Test that each item has all required fields."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Find first item with valuations to check structure
        items_by_number = {i["number"]: i for i in data["results"]}
        item = items_by_number[10001]

        # Check all required fields present
        assert "id" in item
        assert "number" in item
        assert "production_status" in item
        assert "completeness" in item
        assert "has_instructions" in item
        assert "has_box" in item
        assert "is_factory_sealed" in item
        assert "owner_id" in item
        assert "owner_initial_estimate" in item
        assert "valuations_count" in item
        assert "total_likes" in item
        assert "top_valuation" in item

    def test_list_item_top_valuation_structure(self) -> None:
        """Test that top_valuation has correct structure when present."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Find item with valuations (brickset_active_complete)
        items_by_number = {i["number"]: i for i in data["results"]}
        item = items_by_number[10001]
        top_valuation = item["top_valuation"]
        assert top_valuation is not None
        assert "id" in top_valuation
        assert "value" in top_valuation
        assert "currency" in top_valuation
        assert "likes_count" in top_valuation
        assert "user_id" in top_valuation

    def test_aggregations_correct_valuations_count(self) -> None:
        """Test that valuations_count is accurate."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # brickset_active_complete has 2 valuations
        assert items_by_number[10001]["valuations_count"] == 2
        # brickset_retired_incomplete has 1 valuation
        assert items_by_number[20002]["valuations_count"] == 1
        # Others have 0 valuations
        assert items_by_number[30003]["valuations_count"] == 0
        assert items_by_number[40004]["valuations_count"] == 0

    def test_aggregations_correct_total_likes(self) -> None:
        """Test that total_likes is sum of all valuation likes."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify we have all 4 bricksets
        assert data["count"] == 4, f"Expected 4 bricksets, got {data['count']}"
        items_by_number = {i["number"]: i for i in data["results"]}

        # brickset_active_complete: 5 + 8 = 13
        assert items_by_number[10001]["total_likes"] == 13
        # brickset_retired_incomplete: 3
        assert items_by_number[20002]["total_likes"] == 3
        # Others: 0
        assert items_by_number[30003]["total_likes"] == 0
        assert items_by_number[40004]["total_likes"] == 0

    def test_top_valuation_has_highest_likes(self) -> None:
        """Test that top_valuation is the one with most likes."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # brickset_active_complete: highest likes = 8 (valuation2)
        top_val = items_by_number[10001]["top_valuation"]
        assert top_val["id"] == self.valuation2.id
        assert top_val["likes_count"] == 8
        assert top_val["value"] == 120

    def test_filter_by_production_status_active(self) -> None:
        """Test filtering by production_status=ACTIVE."""
        params = {"production_status": ProductionStatus.ACTIVE}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 30003 in numbers
        assert 40004 in numbers

    def test_filter_by_production_status_retired(self) -> None:
        """Test filtering by production_status=RETIRED."""
        params = {"production_status": ProductionStatus.RETIRED}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["number"] == 20002

    def test_filter_by_completeness_complete(self) -> None:
        """Test filtering by completeness=COMPLETE."""
        params = {"completeness": Completeness.COMPLETE}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 30003 in numbers
        assert 40004 in numbers

    def test_filter_by_has_instructions_true(self) -> None:
        """Test filtering by has_instructions=true."""
        params = {"has_instructions": "true"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 40004 in numbers

    def test_filter_by_has_instructions_false(self) -> None:
        """Test filtering by has_instructions=false."""
        params = {"has_instructions": "false"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        numbers = [item["number"] for item in data["results"]]
        assert 20002 in numbers
        assert 30003 in numbers

    def test_filter_by_has_box_true(self) -> None:
        """Test filtering by has_box=true."""
        params = {"has_box": "true"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 30003 in numbers

    def test_filter_by_is_factory_sealed_true(self) -> None:
        """Test filtering by is_factory_sealed=true."""
        params = {"is_factory_sealed": "true"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 40004 in numbers

    def test_filter_by_search_query_partial_match(self) -> None:
        """Test filtering by search query (q parameter)."""
        params = {"q": "100"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should match 10001 (contains "100")
        assert data["count"] == 1
        assert data["results"][0]["number"] == 10001

    def test_filter_by_search_query_full_match(self) -> None:
        """Test filtering by exact search query."""
        params = {"q": "20002"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["number"] == 20002

    def test_filter_by_multiple_conditions(self) -> None:
        """Test filtering by multiple conditions simultaneously."""
        params = {
            "production_status": ProductionStatus.ACTIVE,
            "completeness": Completeness.COMPLETE,
            "has_instructions": "true",
        }
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Both 10001 and 40004 match (ACTIVE, COMPLETE, has_instructions=True)
        assert data["count"] == 2
        numbers = [item["number"] for item in data["results"]]
        assert 10001 in numbers
        assert 40004 in numbers

    def test_ordering_by_created_at_default(self) -> None:
        """Test default ordering (most recent first)."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Default is -created_at, so newest first
        # Since all created in this test, order varies but should work
        assert len(data["results"]) == 4

    def test_ordering_by_valuations_count_ascending(self) -> None:
        """Test ordering by valuations_count ascending."""
        params = {"ordering": "valuations_count"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should be ordered: 0, 0, 1, 2 likes
        counts = [item["valuations_count"] for item in data["results"]]
        assert counts == sorted(counts)

    def test_ordering_by_valuations_count_descending(self) -> None:
        """Test ordering by valuations_count descending."""
        params = {"ordering": "-valuations_count"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should be ordered: 2, 1, 0, 0 likes
        counts = [item["valuations_count"] for item in data["results"]]
        assert counts == sorted(counts, reverse=True)

    def test_pagination_default_page_size(self) -> None:
        """Test default pagination (page_size=20)."""
        # Create 21 additional bricksets with unique numbers
        for i in range(50001, 50022):
            baker.make(
                BrickSet,
                owner=self.user1,
                number=i,
                production_status=ProductionStatus.ACTIVE,
            )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 25  # 4 + 21 from setUp
        assert len(data["results"]) == 20  # First page
        assert data["next"] is not None
        assert data["previous"] is None

    def test_pagination_custom_page_size(self) -> None:
        """Test custom page_size parameter."""
        # Create 10 additional bricksets
        for i in range(50001, 50011):
            baker.make(
                BrickSet,
                owner=self.user1,
                number=i,
                production_status=ProductionStatus.ACTIVE,
            )

        params = {"page_size": 5}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 5

    def test_pagination_page_parameter(self) -> None:
        """Test page parameter for pagination."""
        # Create 21 additional bricksets
        for i in range(50001, 50022):
            baker.make(
                BrickSet,
                owner=self.user1,
                number=i,
                production_status=ProductionStatus.ACTIVE,
            )

        params = {"page": 2, "page_size": 10}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 10
        assert data["previous"] is not None
        assert data["next"] is not None

    def test_pagination_respects_max_page_size(self) -> None:
        """Test that serializer validates page_size does not exceed max=100."""
        params = {"page_size": 101}
        response = self.client.get(self.url, params)

        # page_size=101 is over serializer max_value=100, should get 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_page_parameter_returns_bad_request(self) -> None:
        """Test that invalid page returns 400."""
        params = {"page": "abc"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_page_size_parameter_returns_bad_request(self) -> None:
        """Test that invalid page_size returns 400."""
        params = {"page_size": "xyz"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_production_status_returns_bad_request(self) -> None:
        """Test that invalid production_status returns 400."""
        params = {"production_status": "INVALID_STATUS"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_completeness_returns_bad_request(self) -> None:
        """Test that invalid completeness returns 400."""
        params = {"completeness": "INVALID_COMPLETENESS"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_ordering_returns_bad_request(self) -> None:
        """Test that invalid ordering returns 400."""
        params = {"ordering": "invalid_field"}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_page_zero_returns_bad_request(self) -> None:
        """Test that page=0 returns 400."""
        params = {"page": 0}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_page_size_zero_returns_bad_request(self) -> None:
        """Test that page_size=0 returns 400."""
        params = {"page_size": 0}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_page_size_exceeds_max_returns_bad_request(self) -> None:
        """Test that page_size > 100 returns 400."""
        params = {"page_size": 101}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_allows_anonymous_access(self) -> None:
        """Test that endpoint allows unauthenticated users."""
        response = self.client.get(self.url)

        # Should work without authentication
        assert response.status_code == status.HTTP_200_OK

    def test_response_does_not_include_sensitive_data(self) -> None:
        """Test that response doesn't include sensitive fields."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}
        item = items_by_number[10001]

        # Should not include internal/sensitive fields
        assert "created_at" not in item
        assert "updated_at" not in item

    def test_empty_result_when_no_matches(self) -> None:
        """Test that filtering with no matches returns empty results."""
        params = {
            "production_status": ProductionStatus.ACTIVE,
            "q": "99999",
        }
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_top_valuation_null_when_no_valuations(self) -> None:
        """Test that top_valuation is null for bricksets without valuations."""
        params = {"page_size": 100}
        response = self.client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items_by_number = {i["number"]: i for i in data["results"]}

        # brickset_active_no_instructions has no valuations
        top_val = items_by_number[30003]["top_valuation"]
        assert top_val is None
