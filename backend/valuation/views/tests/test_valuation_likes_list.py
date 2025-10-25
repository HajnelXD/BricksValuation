"""API integration tests for Valuation likes list endpoint."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import BrickSet, Completeness, ProductionStatus
from valuation.models import Like, Valuation

User = get_user_model()


class TestValuationLikesListView(APITestCase):
    """Test ValuationLikesListView GET /api/v1/valuations/{id}/likes endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.liker1 = baker.make(User)
        self.liker2 = baker.make(User)
        self.liker3 = baker.make(User)
        self.valuation_author = baker.make(User)
        self.other_author = baker.make(User)
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

        self.valuation = Valuation.valuations.create(
            user=self.valuation_author,
            brickset=self.brickset,
            value=450,
            currency="PLN",
        )

        self.other_valuation = Valuation.valuations.create(
            user=self.other_author,
            brickset=self.other_brickset,
            value=500,
            currency="PLN",
        )

        self.url = reverse_lazy(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

    def test_get_successfully_returns_ok_status(self) -> None:
        """GET with valid valuation_id returns 200."""
        Like.objects.create(user=self.liker1, valuation=self.valuation)
        self.client.force_authenticate(user=self.liker1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_response_has_pagination_structure(self) -> None:
        """GET response has count, next, previous, and results."""
        Like.objects.create(user=self.liker1, valuation=self.valuation)
        self.client.force_authenticate(user=self.liker1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)

    def test_get_returns_only_likes_for_specified_valuation(self) -> None:
        """GET returns only likes for the specified Valuation."""
        like1 = Like.objects.create(user=self.liker1, valuation=self.valuation)
        like2 = Like.objects.create(user=self.liker2, valuation=self.valuation)
        # Like on different valuation - should not appear
        Like.objects.create(user=self.liker1, valuation=self.other_valuation)

        self.client.force_authenticate(user=self.liker1)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        result_ids = [item["user_id"] for item in data["results"]]
        assert like1.user_id in result_ids
        assert like2.user_id in result_ids

    def test_get_orders_by_created_at_descending(self) -> None:
        """GET returns likes ordered by -created_at (newest first)."""
        like1 = Like.objects.create(user=self.liker1, valuation=self.valuation)
        like2 = Like.objects.create(user=self.liker2, valuation=self.valuation)
        like3 = Like.objects.create(user=self.liker3, valuation=self.valuation)

        self.client.force_authenticate(user=self.liker1)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data["results"]
        assert len(results) == 3
        # Newest first (like3 created last)
        assert results[0]["user_id"] == like3.user_id
        assert results[1]["user_id"] == like2.user_id
        assert results[2]["user_id"] == like1.user_id

    def test_get_list_item_has_all_required_fields(self) -> None:
        """GET list item includes all LikeListItemDTO fields."""
        Like.objects.create(user=self.liker1, valuation=self.valuation)
        self.client.force_authenticate(user=self.liker1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item = data["results"][0]
        assert "user_id" in item
        assert "created_at" in item
        # Verify excluded fields
        assert "valuation_id" not in item
        assert "updated_at" not in item

    def test_get_returns_empty_list_for_valuation_without_likes(self) -> None:
        """GET returns empty results for Valuation with no likes."""
        self.client.force_authenticate(user=self.liker1)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert len(data["results"]) == 0

    def test_get_returns_not_found_for_nonexistent_valuation(self) -> None:
        """GET with non-existent valuation_id returns 404."""
        self.client.force_authenticate(user=self.liker1)
        nonexistent_id = 999999
        url = reverse_lazy(
            "valuation:valuation-like",
            kwargs={"valuation_id": nonexistent_id},
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
        # Create multiple likes
        for i in range(25):
            user = baker.make(User)
            Like.objects.create(user=user, valuation=self.valuation)

        self.client.force_authenticate(user=self.liker1)

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
        assert len(data2["results"]) == 5
        assert data2["next"] is None
        assert data2["previous"] is not None

    def test_get_pagination_with_custom_page_size(self) -> None:
        """GET respects page_size query parameter."""
        for i in range(15):
            user = baker.make(User)
            Like.objects.create(user=user, valuation=self.valuation)

        self.client.force_authenticate(user=self.liker1)
        response = self.client.get(self.url, {"page": 1, "page_size": 10})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 10
        assert data["next"] is not None

    def test_get_with_authenticated_user_can_view_likes(self) -> None:
        """GET with authenticated user successfully retrieves likes."""
        Like.objects.create(user=self.liker1, valuation=self.valuation)
        self.client.force_authenticate(user=self.valuation_author)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1

    def test_get_user_can_view_likes_on_their_own_valuation(self) -> None:
        """GET allows valuation author to view likes on their own valuation."""
        Like.objects.create(user=self.liker1, valuation=self.valuation)
        self.client.force_authenticate(user=self.valuation_author)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["user_id"] == self.liker1.id
