"""Tests for ValuationLikeView API endpoint."""
from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from account.models import User
from catalog.models import BrickSet, Completeness, ProductionStatus
from valuation.models import Like, Valuation


class ValuationLikeViewTests(APITestCase):
    """Test cases for POST /valuations/{valuation_id}/likes endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test users
        self.liker = User.objects.create_user(
            username="liker",
            email="liker@example.com",
            password="likerpass123",
        )
        self.valuation_author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="authorpass123",
        )
        self.brickset_owner = User.objects.create_user(
            username="brickset_owner",
            email="brickset_owner@example.com",
            password="ownerpass123",
        )

        # Create test brickset
        self.brickset = BrickSet.objects.create(
            number=70620,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner=self.brickset_owner,
        )

        # Create test valuation
        self.valuation = Valuation.valuations.create(
            user=self.valuation_author,
            brickset=self.brickset,
            value=500,
            currency="PLN",
            comment="Great condition",
        )

        # Authenticate as liker
        self.client.force_authenticate(user=self.liker)

    def test_post_like_success_returns_created_with_like_data(self) -> None:
        """Test successful POST returns 201 Created with like data."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["valuation_id"] == self.valuation.id
        assert data["user_id"] == self.liker.id
        assert "created_at" in data

        # Verify Like was persisted
        like = Like.objects.get(user=self.liker, valuation=self.valuation)
        assert like.id is not None

    def test_post_like_includes_timestamp_in_response(self) -> None:
        """Test that response includes created_at timestamp."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.post(url, data={}, format="json")

        data = response.json()
        assert data["created_at"] is not None
        # Validate ISO format timestamp
        assert "T" in data["created_at"]
        assert "Z" in data["created_at"] or "+" in data["created_at"]

    def test_post_like_own_valuation_returns_forbidden(self) -> None:
        """Test POST returns 403 when user tries to like own valuation."""
        # Re-authenticate as valuation author
        self.client.force_authenticate(user=self.valuation_author)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "Cannot like your own valuation" in data["detail"]

    def test_post_like_nonexistent_valuation_returns_not_found(self) -> None:
        """Test POST returns 404 when valuation doesn't exist."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": 999999},
        )
        response = self.client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Valuation with id 999999 not found" in data["detail"]

    def test_post_like_duplicate_returns_conflict(self) -> None:
        """Test POST returns 409 when user already liked valuation."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # Create first like
        response1 = self.client.post(url, data={}, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Attempt duplicate like
        response2 = self.client.post(url, data={}, format="json")

        assert response2.status_code == status.HTTP_409_CONFLICT
        data = response2.json()
        assert "already exists" in data["detail"]

    def test_post_like_unauthenticated_returns_unauthorized(self) -> None:
        """Test POST returns 401 when user is not authenticated."""
        self.client.force_authenticate(user=None)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Authentication credentials were not provided" in data["detail"]

    def test_post_like_multiple_users_same_valuation_succeeds(self) -> None:
        """Test that multiple different users can like same valuation."""
        third_user = User.objects.create_user(
            username="third",
            email="third@example.com",
            password="thirdpass123",
        )

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # First user likes
        response1 = self.client.post(url, data={}, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Third user likes same valuation
        self.client.force_authenticate(user=third_user)
        response2 = self.client.post(url, data={}, format="json")
        assert response2.status_code == status.HTTP_201_CREATED

        # Verify both likes exist
        assert Like.objects.filter(valuation=self.valuation).count() == 2

    def test_post_like_with_empty_body_succeeds(self) -> None:
        """Test POST succeeds even with empty request body."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # Send POST with truly empty body
        response = self.client.post(url, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["valuation_id"] == self.valuation.id
        assert data["user_id"] == self.liker.id

    def test_post_like_response_has_correct_field_types(self) -> None:
        """Test response fields have correct data types."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.post(url, data={}, format="json")

        data = response.json()
        assert isinstance(data["valuation_id"], int)
        assert isinstance(data["user_id"], int)
        assert isinstance(data["created_at"], str)
