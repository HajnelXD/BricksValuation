"""Tests for BrickSetDeleteView DELETE endpoint."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from catalog.models import BrickSet, Completeness, ProductionStatus
from catalog.views.brickset_detail_update import BrickSetDetailUpdateView
from valuation.models import Valuation

User = get_user_model()


class BrickSetDeleteViewTests(TestCase):
    """Test BrickSetDetailUpdateView DELETE method endpoint."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view_class = BrickSetDetailUpdateView
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="testpass123",
        )
        self.brickset = BrickSet.objects.create(
            owner=self.owner,
            number=12345,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=True,
            has_box=True,
            is_factory_sealed=False,
            owner_initial_estimate=250,
        )

    def _delete(self, brickset_id, user=None):
        """Helper to send DELETE request."""
        view = self.view_class.as_view()
        url = f"/api/v1/bricksets/{brickset_id}/"
        request = self.factory.delete(url)
        if user:
            force_authenticate(request, user=user)
        response = view(request, pk=brickset_id)
        response.render()
        return response

    def test_unauthenticated_returns_401(self):
        """Unauthenticated DELETE should return 401."""
        response = self._delete(self.brickset.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_not_found_returns_404(self):
        """DELETE of non-existent BrickSet should return 404."""
        response = self._delete(99999, self.owner)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.data

    def test_not_owner_returns_403(self):
        """DELETE by non-owner should return 403 with reason."""
        response = self._delete(self.brickset.id, self.other_user)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get("reason") == "not_owner"
        assert "detail" in response.data

    def test_successful_delete_returns_204(self):
        """Owner can delete BrickSet without valuations."""
        response = self._delete(self.brickset.id, self.owner)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_removes_from_database(self):
        """DELETE should remove BrickSet from database."""
        brickset_id = self.brickset.id
        self._delete(brickset_id, self.owner)
        with self.assertRaises(BrickSet.DoesNotExist):
            BrickSet.bricksets.get(pk=brickset_id)

    def test_rb_01_other_valuations_forbidden(self):
        """Delete should fail if other users' valuations exist (RB-01)."""
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.other_user,
            value=100,
        )
        response = self._delete(self.brickset.id, self.owner)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get("reason") == "other_users_valuations_exist"
        # BrickSet should still exist in DB
        assert BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_rb_01_owner_likes_forbidden(self):
        """Delete should fail if owner's valuation has likes (RB-01)."""
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=200,
        )
        valuation.likes_count = 5
        valuation.save()
        response = self._delete(self.brickset.id, self.owner)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get("reason") == "owner_valuation_has_likes"
        # BrickSet should still exist in DB
        assert BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_rb_01_owner_zero_likes_allowed(self):
        """Delete should succeed if owner's valuation has 0 likes (RB-01)."""
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=200,
        )
        valuation.likes_count = 0
        valuation.save()
        response = self._delete(self.brickset.id, self.owner)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # BrickSet should be deleted
        assert not BrickSet.bricksets.filter(pk=self.brickset.id).exists()

    def test_delete_cascades_valuations(self):
        """DELETE should cascade and remove related valuations."""
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=200,
        )
        valuation_id = valuation.id
        brickset_id = self.brickset.id
        response = self._delete(brickset_id, self.owner)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # BrickSet should be deleted
        assert not BrickSet.bricksets.filter(pk=brickset_id).exists()
        # Valuation should be cascade deleted
        assert not Valuation.valuations.filter(pk=valuation_id).exists()

    def test_delete_response_has_no_body(self):
        """DELETE response should have empty body for 204."""
        response = self._delete(self.brickset.id, self.owner)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # 204 response body should be empty
        assert response.content == b""
