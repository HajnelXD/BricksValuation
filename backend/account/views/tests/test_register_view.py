"""Tests for the register user API view."""
from __future__ import annotations

from datetime import datetime

from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from account.models import User
from account.views.register import RegisterUserView

USERNAME_FIELD = "username"
EMAIL_FIELD = "email"
PASSWORD_FIELD = "password"
ERRORS_FIELD = "errors"
CREATED_AT_FIELD = "created_at"
DETAIL_FIELD = "detail"
FIELD_FIELD = "field"

DEFAULT_USERNAME = "new_user"
DEFAULT_EMAIL = "new_user@example.com"
DEFAULT_PASSWORD = "Secur3Pass!"
INVALID_USERNAME = "invalid username"
INVALID_EMAIL = "space_user@example.com"
CONFLICT_USERNAME = "existing"
CONFLICT_EMAIL = "duplicate@example.com"


class RegisterUserViewTests(APITestCase):
    """Ensure the registration endpoint behaves as expected."""

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.view = RegisterUserView.as_view()
        self.url = reverse_lazy("auth-register")

    def test_register_success_returns_profile(self) -> None:
        payload = {
            USERNAME_FIELD: DEFAULT_USERNAME,
            EMAIL_FIELD: DEFAULT_EMAIL,
            PASSWORD_FIELD: DEFAULT_PASSWORD,
        }

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_201_CREATED
        response_body = response.data
        assert response_body[USERNAME_FIELD] == payload[USERNAME_FIELD]
        assert response_body[EMAIL_FIELD] == payload[EMAIL_FIELD]
        assert CREATED_AT_FIELD in response_body
        created_at_value = response_body[CREATED_AT_FIELD]
        if isinstance(created_at_value, datetime):
            assert "T" in created_at_value.isoformat()
        else:
            assert "T" in str(created_at_value)
        assert User.objects.filter(username=payload[USERNAME_FIELD]).exists()

    def test_register_invalid_username_relayed(self) -> None:
        payload = {
            USERNAME_FIELD: INVALID_USERNAME,
            EMAIL_FIELD: INVALID_EMAIL,
            PASSWORD_FIELD: "AnotherSecur3Pass!",
        }

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_body = response.data
        assert ERRORS_FIELD in response_body
        assert USERNAME_FIELD in response_body[ERRORS_FIELD]

    def test_register_conflict_when_username_exists(self) -> None:
        User.objects.create_user(
            username=CONFLICT_USERNAME,
            email="existing@example.com",
            password="P@ssw0rd123",
        )

        payload = {
            USERNAME_FIELD: CONFLICT_USERNAME,
            EMAIL_FIELD: CONFLICT_EMAIL,
            PASSWORD_FIELD: "SomeSecur3Pass!",
        }

        request = self.factory.post(self.url, payload, format="json")
        response = self.view(request)
        response.render()

        assert response.status_code == status.HTTP_409_CONFLICT
        response_body = response.data
        assert response_body[FIELD_FIELD] == USERNAME_FIELD
        assert DETAIL_FIELD in response_body
