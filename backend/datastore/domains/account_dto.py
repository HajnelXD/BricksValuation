"""Account domain DTO & command models.

Each dataclass mirrors API contract segments defined in `.ai/api-plan.md` for
user related endpoints while referencing underlying Django model fields.

All dataclasses use `slots=True` to reduce memory overhead and prevent dynamic
attribute creation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional

from account.models import User


@dataclass(slots=True)
class RegisterUserCommand:
    """Input payload for `POST /auth/register`.

    Direct mapping to expected request JSON body. Password is kept here only
    for command handling; it will never appear in any outward DTO.
    """

    source_model: ClassVar[type[User]] = User

    username: str
    email: str
    password: str  # raw password (will be hashed by service layer)


@dataclass(slots=True)
class LoginCommand:
    """Input payload for `POST /auth/login`.

    Used purely for authentication evaluation; not persisted beyond auth logic.
    """

    username: str
    password: str


@dataclass(slots=True)
class UserRefDTO:
    """Minimal user reference used inside other DTOs (e.g., login response).

    Excludes timestamps to keep nested payloads lean.
    """

    source_model: ClassVar[type[User]] = User

    id: int
    username: str
    email: str


@dataclass(slots=True)
class UserProfileDTO:
    """Full user profile as returned by `/auth/me` and registration success.

    `created_at` exposed; `updated_at` intentionally omitted from public API.
    """

    source_model: ClassVar[type[User]] = User

    id: int
    username: str
    email: str
    created_at: datetime


@dataclass(slots=True)
class LoginSuccessDTO:
    """Login success envelope.

    Contains both user reference and optionally token. Token can be `None` if
    only cookie is set and body omits token (configuration dependent).
    """

    user: UserRefDTO
    token: Optional[str] = None
