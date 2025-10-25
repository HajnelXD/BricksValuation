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


class ValuationUnlikeViewTests(APITestCase):
    """Test cases for DELETE /valuations/{valuation_id}/likes endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test users
        self.liker = User.objects.create_user(
            username="liker",
            email="liker@example.com",
            password="likerpass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="otherpass123",
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

        # Create a like from liker on valuation
        self.like = Like.objects.create(
            user=self.liker,
            valuation=self.valuation,
        )

        # Authenticate as liker
        self.client.force_authenticate(user=self.liker)

    def test_delete_like_success_returns_no_content(self) -> None:
        """Test successful DELETE returns 204 No Content."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # 204 response should have empty body
        assert response.content == b"" or response.data is None

        # Verify Like was deleted from database
        assert not Like.objects.filter(user=self.liker, valuation=self.valuation).exists()

    def test_delete_like_not_found_returns_not_found(self) -> None:
        """Test DELETE returns 404 when like doesn't exist."""
        # Authenticate as different user who never liked
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
        assert str(self.valuation.id) in data["detail"]
        assert str(self.other_user.id) in data["detail"]

        # Original like should still exist
        assert Like.objects.filter(user=self.liker, valuation=self.valuation).exists()

    def test_delete_like_unauthenticated_returns_unauthorized(self) -> None:
        """Test DELETE returns 401 when user is not authenticated."""
        self.client.force_authenticate(user=None)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Authentication credentials were not provided" in data["detail"]

    def test_delete_like_only_own_like_succeeds(self) -> None:
        """Test that user can only delete their own like (implicit authorization)."""
        # Create like from other user
        other_like = Like.objects.create(
            user=self.other_user,
            valuation=self.valuation,
        )

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # Liker deletes their own like
        response = self.client.delete(url, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Liker's like should be deleted
        assert not Like.objects.filter(user=self.liker, valuation=self.valuation).exists()

        # Other user's like should still exist
        assert Like.objects.filter(pk=other_like.id).exists()

    def test_delete_like_idempotent_second_call_returns_not_found(self) -> None:
        """Test that second DELETE call on same like returns 404 (not idempotent)."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # First DELETE succeeds
        response1 = self.client.delete(url, format="json")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        # Like should be deleted from DB
        assert not Like.objects.filter(
            user=self.liker,
            valuation=self.valuation,
        ).exists()

        # Second DELETE should return 404
        response2 = self.client.delete(url, format="json")
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        data = response2.json()
        assert "not found" in data["detail"].lower()

    def test_delete_like_removes_only_target_like(self) -> None:
        """Test DELETE only removes specific like, not all likes on valuation."""
        # Create another like from different user
        third_user = User.objects.create_user(
            username="third",
            email="third@example.com",
            password="thirdpass123",
        )
        third_like = Like.objects.create(
            user=third_user,
            valuation=self.valuation,
        )

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # Liker deletes their like
        response = self.client.delete(url, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Liker's like should be deleted
        assert not Like.objects.filter(user=self.liker, valuation=self.valuation).exists()

        # Third user's like should still exist
        assert Like.objects.filter(pk=third_like.id).exists()

    def test_delete_like_response_has_no_body(self) -> None:
        """Test 204 response should have empty body."""
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # 204 No Content should have empty body
        assert response.content == b""

    def test_delete_like_nonexistent_valuation_returns_not_found(self) -> None:
        """Test DELETE returns 404 when valuation doesn't exist.

        Note: This tests the implicit behavior - service layer tries to get
        like with nonexistent valuation_id, and returns 404.
        """
        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": 999999},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_like_different_user_cannot_remove(self) -> None:
        """Test that different user cannot remove another user's like."""
        # Authenticate as different user
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )

        # Try to delete liker's like as different user
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Original like should still exist (implicit authorization)
        assert Like.objects.filter(user=self.liker, valuation=self.valuation).exists()

    def test_delete_like_response_error_format(self) -> None:
        """Test 404 response error format."""
        # Try to delete non-existent like
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "valuation:valuation-like",
            kwargs={"valuation_id": self.valuation.id},
        )
        response = self.client.delete(url, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0
