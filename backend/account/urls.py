"""URL configuration for account API endpoints."""
from __future__ import annotations

from django.urls import path

from account.views.register import RegisterUserView

urlpatterns = [
    path("auth/register", RegisterUserView.as_view(), name="auth-register"),
]
