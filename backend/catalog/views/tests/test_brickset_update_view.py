"""Tests for BrickSetUpdateView PATCH endpoint."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from catalog.models import BrickSet, Completeness, ProductionStatus
from catalog.views.brickset_update import BrickSetUpdateView
from valuation.models import Valuation

User = get_user_model()


class BrickSetUpdateViewTests(TestCase):
    """Test BrickSetUpdateView PATCH endpoint."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = BrickSetUpdateView.as_view()
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

    def _patch(self, brickset_id, data, user=None):
        url = f"/api/v1/bricksets/{brickset_id}/"
        request = self.factory.patch(url, data, format="json")
        if user:
            force_authenticate(request, user=user)
        response = self.view(request, pk=brickset_id)
        response.render()
        return response

    def test_unauthenticated_returns_401(self):
        response = self._patch(self.brickset.id, {"has_box": False})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_found_returns_404(self):
        response = self._patch(99999, {"has_box": False}, self.owner)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_owner_returns_403(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.other_user,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data.get("reason") == "not_owner"

    def test_update_has_box(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        self.brickset.refresh_from_db()
        assert not self.brickset.has_box

    def test_update_owner_estimate(self):
        response = self._patch(
            self.brickset.id,
            {"owner_initial_estimate": 500},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        self.brickset.refresh_from_db()
        assert self.brickset.owner_initial_estimate == 500

    def test_update_both(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False, "owner_initial_estimate": 300},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        self.brickset.refresh_from_db()
        assert not self.brickset.has_box
        assert self.brickset.owner_initial_estimate == 300

    def test_response_has_required_fields(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        required = [
            "id", "number", "production_status", "completeness",
            "has_instructions", "has_box", "is_factory_sealed",
            "owner_initial_estimate", "owner_id", "valuations",
            "valuations_count", "total_likes",
        ]
        for field in required:
            assert field in response.data

    def test_response_valuations_empty(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("valuations") == []
        assert response.data.get("valuations_count") == 0
        assert response.data.get("total_likes") == 0

    def test_empty_payload_returns_400(self):
        response = self._patch(self.brickset.id, {}, self.owner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_has_box_returns_400(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": 123},
            self.owner,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_estimate_too_low_returns_400(self):
        response = self._patch(
            self.brickset.id,
            {"owner_initial_estimate": 0},
            self.owner,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_estimate_too_high_returns_400(self):
        response = self._patch(
            self.brickset.id,
            {"owner_initial_estimate": 1000000},
            self.owner,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rb_01_other_valuations_forbidden(self):
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.other_user,
            value=100,
        )
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.assertEqual(
            response.data.get("reason"),
            "other_users_valuations_exist",
        )

    def test_rb_01_owner_likes_forbidden(self):
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=200,
        )
        valuation.likes_count = 5
        valuation.save()
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.assertEqual(
            response.data.get("reason"),
            "owner_valuation_has_likes",
        )

    def test_rb_01_owner_zero_likes_allowed(self):
        valuation = Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=200,
        )
        valuation.likes_count = 0
        valuation.save()
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_response_includes_valuations(self):
        Valuation.valuations.create(
            brickset=self.brickset,
            user=self.owner,
            value=300,
        )
        response = self._patch(
            self.brickset.id,
            {"owner_initial_estimate": 350},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("valuations", [])) == 1
        assert response.data["valuations"][0]["value"] == 300
        assert response.data.get("valuations_count") == 1
        assert response.data.get("total_likes") == 0

    def test_aggregates_single(self):
        bs2 = BrickSet.objects.create(
            owner=self.owner,
            number=54321,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=True,
            owner_initial_estimate=100,
        )
        Valuation.valuations.create(
            brickset=bs2,
            user=self.owner,
            value=150,
        )
        response = self._patch(bs2.id, {"has_box": True}, self.owner)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("valuations_count") == 1
        assert response.data.get("total_likes") == 0

    def test_aggregates_multiple(self):
        bs2 = BrickSet.objects.create(
            owner=self.owner,
            number=54321,
            production_status=ProductionStatus.ACTIVE,
            completeness=Completeness.COMPLETE,
            has_instructions=False,
            has_box=False,
            is_factory_sealed=True,
            owner_initial_estimate=100,
        )
        # Single owner valuation with zero likes (allowed to edit)
        val1 = Valuation.valuations.create(
            brickset=bs2,
            user=self.owner,
            value=100,
        )
        assert val1.likes_count == 0  # default
        response = self._patch(bs2.id, {"has_box": True}, self.owner)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("valuations_count") == 1
        assert response.data.get("total_likes") == 0

    def test_no_sensitive_fields(self):
        response = self._patch(
            self.brickset.id,
            {"has_box": False},
            self.owner,
        )
        assert response.status_code == status.HTTP_200_OK
        # These fields SHOULD be in response (they're not sensitive for detail view)
        assert "created_at" in response.data
        assert "updated_at" in response.data
