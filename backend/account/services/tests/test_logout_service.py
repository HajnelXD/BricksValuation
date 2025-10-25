"""Tests for logout service."""
from __future__ import annotations

import logging
from unittest.mock import patch

from django.test import TestCase

from account.services.logout_service import LogoutService


class LogoutServiceTests(TestCase):
    """Test suite for LogoutService."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = LogoutService()
        self.user_id = 1
        self.username = "testuser"

    def test_execute_completes_successfully(self) -> None:
        """execute() should complete without raising exceptions."""
        logout_result = self.service.execute(
            user_id=self.user_id,
            username=self.username,
        )

        assert logout_result is None

    @patch("account.services.logout_service.logger")
    def test_execute_logs_logout_event(self, mock_logger: logging.Logger) -> None:
        """execute() should log logout event with user info."""
        self.service.execute(
            user_id=self.user_id,
            username=self.username,
        )

        assert mock_logger.info.call_count == 1
        call_args = mock_logger.info.call_args[0][0]
        assert self.username in call_args
        assert str(self.user_id) in call_args
        assert "logged out" in call_args.lower()

    @patch("account.services.logout_service.logger")
    def test_execute_with_different_user_data(self, mock_logger: logging.Logger) -> None:
        """execute() should log correct user data."""
        different_user_id = 42
        different_username = "anotheruser"

        self.service.execute(
            user_id=different_user_id,
            username=different_username,
        )

        assert mock_logger.info.call_count == 1
        call_args = mock_logger.info.call_args[0][0]
        assert different_username in call_args
        assert str(different_user_id) in call_args
