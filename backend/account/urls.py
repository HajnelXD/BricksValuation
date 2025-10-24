"""URL configuration for account API endpoints."""
from __future__ import annotations

from django.urls import path

from account.views.register import RegisterUserView
from account.views.login import LoginView
from account.views.logout import LogoutView

urlpatterns = [
    path("auth/register", RegisterUserView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
]
