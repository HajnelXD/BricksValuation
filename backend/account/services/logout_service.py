"""Service implementing user logout flow.

Handles logout business logic: logging events, validation, and cleanup.
Main responsibility is audit trail for tracking user logouts.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class LogoutService:
    """Coordinate the logout process for an authenticated user."""

    def execute(self, user_id: int, username: str) -> None:
        """Process logout and log the event.

        Args:
            user_id: Unique user identifier.
            username: User's username for audit logging.

        Returns:
            None (void operation).

        Notes:
            This is a thin service layer focused on logging. In the future,
            this could be extended to:
            - Invalidate tokens in Redis/token blacklist
            - Log to audit system
            - Trigger analytics events
            - Clean up session data
        """
        # Log logout event for audit trail
        logger.info(f"User {username} (ID: {user_id}) logged out")
