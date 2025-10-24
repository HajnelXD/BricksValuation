"""JWT configuration for token generation and validation.

This module centralizes JWT settings used by TokenProvider and authentication
middleware. All values can be overridden via Django settings if needed.
"""
from __future__ import annotations

from django.conf import settings

# JWT algorithm - HMAC with SHA-256
ALGORITHM = "HS256"

# Token expiration in seconds (24 hours)
EXPIRATION_SECONDS = 86400

# Secret key for signing tokens (uses Django SECRET_KEY by default)
SECRET_KEY = getattr(settings, "SECRET_KEY", "")

# Cookie configuration for token storage
COOKIE_NAME = "jwt_token"
COOKIE_MAX_AGE = EXPIRATION_SECONDS
COOKIE_SECURE = getattr(settings, "SECURE_SSL_REDIRECT", False)  # True in production
COOKIE_HTTP_ONLY = True
COOKIE_SAME_SITE = "Strict"
