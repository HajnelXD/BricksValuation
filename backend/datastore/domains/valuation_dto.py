"""Valuation & Like domain DTO & command models.

Encapsulates request and response payload structures for valuation and like
related endpoints as per API plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional

from valuation.models import Valuation, Like, SystemMetrics

# --------------------------- Command Models ---------------------------

@dataclass(slots=True)
class CreateValuationCommand:
    """Input for `POST /bricksets/{brickset_id}/valuations`.

    `brickset_id` is external path parameter; included here for convenience so
    service layer can operate solely on the command object.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    brickset_id: int
    value: int
    currency: Optional[str] = None  # default logic will substitute 'PLN'
    comment: Optional[str] = None


@dataclass(slots=True)
class LikeValuationCommand:
    """Command for `POST /valuations/{valuation_id}/likes`.

    Body is empty in API spec; valuation_id carried from path.
    """

    source_model: ClassVar[type[Like]] = Like

    valuation_id: int


@dataclass(slots=True)
class UnlikeValuationCommand:
    """Command for `DELETE /valuations/{valuation_id}/likes`.

    Represented for symmetry; may resolve to deletion of Like record.
    """

    source_model: ClassVar[type[Like]] = Like

    valuation_id: int


# ----------------------------- DTO Models -----------------------------

@dataclass(slots=True)
class ValuationDTO:
    """Full valuation representation (create success, detail view).

    Exposes both `created_at` and `updated_at`. `likes_count` is denormalized
    field from model.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    brickset_id: int
    user_id: int
    value: int
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class ValuationListItemDTO:
    """Valuation item for list endpoints (`GET /bricksets/{id}/valuations`).

    Omits `updated_at` for brevity in aggregated listing.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    user_id: int
    value: int
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime


@dataclass(slots=True)
class LikeDTO:
    """Representation of a like create success response.

    Mirrors `POST /valuations/{valuation_id}/likes` success body.
    """

    source_model: ClassVar[type[Like]] = Like

    valuation_id: int
    user_id: int
    created_at: datetime


@dataclass(slots=True)
class LikeListItemDTO:
    """Item for `/valuations/{valuation_id}/likes` list (optional endpoint)."""

    source_model: ClassVar[type[Like]] = Like

    user_id: int
    liked_at: datetime  # mapped from Like.created_at


@dataclass(slots=True)
class OwnedValuationListItemDTO:
    """Item for `/users/me/valuations` list.

    Includes lightweight brickset reference as nested object per API plan.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    brickset: dict  # {"id": int, "number": int}
    value: int
    currency: str
    likes_count: int
    created_at: datetime


# ----------------------------- Metrics DTO ----------------------------

@dataclass(slots=True)
class SystemMetricsDTO:
    """DTO for `/metrics/system`.

    Adds computed ratio fields not stored in model: `serviced_sets_ratio`,
    `active_users_ratio`. These must be derived by service layer using guard
    against division by zero.
    """

    source_model: ClassVar[type[SystemMetrics]] = SystemMetrics

    total_sets: int
    serviced_sets: int
    active_users: int
    serviced_sets_ratio: float
    active_users_ratio: float
    updated_at: datetime

