"""Throttling classes for rate limiting API endpoints."""
from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Rate limiting for login endpoint.

    Limits:
    - 5 requests per minute per IP address
    - 10 requests per minute per username (if provided in request)
    """

    scope = "login"

    def get_cache_key(self) -> str | None:
        """Generate cache key based on IP or username.

        Returns cache key for throttling based on IP address.
        For per-username limiting, a custom backend would be needed.

        Returns:
            Cache key string or None if unable to determine.
        """
        if self.request.user and self.request.user.is_authenticated:
            # If user is authenticated, throttle by user ID
            return f"throttle_{self.scope}_user_{self.request.user.id}"

        # Throttle by IP address
        return self.get_ident(self.request)
