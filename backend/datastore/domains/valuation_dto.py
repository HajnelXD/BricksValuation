"""Valuation & Like domain DTO & command models.  # noqa: WPS202

Encapsulates request and response payload structures for valuation and like
related endpoints as per API plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional

from valuation.models import Like, SystemMetrics, Valuation

# --------------------------- Command Models ---------------------------


@dataclass(slots=True)
class CreateValuationCommand:
    """Input for `POST /bricksets/{brickset_id}/valuations`.

    `brickset_id` is external path parameter; included here for convenience so
    service layer can operate solely on the command object.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    brickset_id: int
    value: int  # noqa: WPS110 - domain field name
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
class CreateLikeCommand:
    """Input for `POST /valuations/{valuation_id}/likes` service layer.

    Extends LikeValuationCommand with user_id from request.user for service processing.
    Combines path parameter (valuation_id) with authenticated user context (user_id).
    """

    source_model: ClassVar[type[Like]] = Like

    valuation_id: int
    user_id: int


@dataclass(slots=True)
class UnlikeValuationCommand:
    """Command for `DELETE /valuations/{valuation_id}/likes`.

    Represented for symmetry; may resolve to deletion of Like record.
    Combines path parameter (valuation_id) with authenticated user context (user_id).
    """

    source_model: ClassVar[type[Like]] = Like

    valuation_id: int
    user_id: int

# ----------------------------- DTO Models -----------------------------


@dataclass(slots=True)
class ValuationDTO:
    """Valuation representation for create success and API payloads.

    `updated_at` can remain unset for list endpoints to keep payload compact.
    Use ValuationDetailDTO for detail endpoints that require full timestamps.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    brickset_id: int
    user_id: int
    value: int  # noqa: WPS110 - domain field name
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


@dataclass(slots=True)
class ValuationDetailDTO:
    """Valuation representation for GET /valuations/{id} detail endpoint.

    Extends ValuationDTO with required updated_at timestamp for detail responses.
    Used exclusively for detail endpoint to keep response complete with all metadata.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    brickset_id: int
    user_id: int
    value: int  # noqa: WPS110 - domain field name
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime
    updated_at: datetime


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
class OwnedValuationListItemDTO:
    """Item for `/users/me/valuations` list.

    Includes lightweight brickset reference as nested object per API plan.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    brickset: dict  # {"id": int, "number": int}
    value: int  # noqa: WPS110 - domain field name
    currency: str
    likes_count: int
    created_at: datetime


@dataclass(slots=True)
class ValuationListItemDTO:
    """Item for `GET /bricksets/{brickset_id}/valuations` list endpoint.

    Memory-efficient DTO for paginated valuation lists. Excludes redundant
    `brickset_id` (already in URL context) and `updated_at` (not needed in list).
    Optimized for high-volume list operations with slots=True.
    """

    source_model: ClassVar[type[Valuation]] = Valuation

    id: int
    user_id: int
    value: int  # noqa: WPS110 - domain field name
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime


@dataclass(slots=True)
class LikeListItemDTO:
    """Item for `GET /valuations/{valuation_id}/likes` list endpoint.

    Memory-efficient DTO for paginated like lists. Contains minimal user reference
    and creation timestamp. Excludes valuation_id (already in URL context) and
    updated_at (not needed in list). Optimized for high-volume list operations
    with slots=True.
    """

    source_model: ClassVar[type[Like]] = Like

    user_id: int
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
