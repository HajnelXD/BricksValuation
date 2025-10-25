"""Catalog (BrickSet) domain DTO & command models.

Bridges API plan brickset endpoints to underlying `BrickSet` & related
`Valuation` aggregation fields. Derived fields annotated accordingly.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional

from catalog.models import BrickSet

# Forward reference to valuation DTO for top valuation summary

# --------------------------- Command Models ---------------------------


@dataclass(slots=True)
class CreateBrickSetCommand:
    """Input for `POST /bricksets`.

    Mirrors request JSON. Owner is implicit from auth context and therefore not
    part of the command payload.
    """

    source_model: ClassVar[type[BrickSet]] = BrickSet

    number: int
    production_status: str  # "ACTIVE" | "RETIRED" (kept as str for API compatibility)
    completeness: str       # "COMPLETE" | "INCOMPLETE"
    has_instructions: bool
    has_box: bool
    is_factory_sealed: bool
    owner_initial_estimate: Optional[int] = None


@dataclass(slots=True)
class UpdateBrickSetCommand:
    """Partial update for `PATCH /bricksets/{id}`.

    Only editable subset per RB-01 rule. All fields optional to allow partial
    updates; validation layer will ensure at least one field provided.
    """

    source_model: ClassVar[type[BrickSet]] = BrickSet

    has_box: Optional[bool] = None
    owner_initial_estimate: Optional[int] = None

# ----------------------------- DTO Models -----------------------------


@dataclass(slots=True)
class TopValuationSummaryDTO:
    """Nested top valuation summary inside brickset list response.

    Derived from the highest liked valuation. Only subset of valuation fields
    required here.
    """

    id: int
    value: int  # noqa: WPS110 - mirrors domain field name
    currency: str
    likes_count: int
    user_id: int


@dataclass(slots=True)
class BrickSetListItemDTO:
    """BrickSet item in list responses (`GET /bricksets`).

    Includes aggregate metrics `valuations_count`, `total_likes` and optional
    `top_valuation` summary for quick glance.
    """

    source_model: ClassVar[type[BrickSet]] = BrickSet

    id: int
    number: int
    production_status: str
    completeness: str
    has_instructions: bool
    has_box: bool
    is_factory_sealed: bool
    owner_id: int
    owner_initial_estimate: Optional[int]
    valuations_count: int  # derived COUNT
    total_likes: int       # derived SUM(likes_count)
    top_valuation: Optional[TopValuationSummaryDTO]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class ValuationInlineDTO:
    """Valuation inline representation for brickset detail.

    Similar to list valuations but excludes `updated_at` for brevity in nested
    context.
    """

    id: int
    user_id: int
    value: int  # noqa: WPS110 - mirrors domain field name
    currency: str
    comment: Optional[str]
    likes_count: int
    created_at: datetime


@dataclass(slots=True)
class BrickSetDetailDTO:
    """Full brickset detail (`GET /bricksets/{id}`).

    Includes valuations array and aggregate counts. `updated_at` present to
    allow client cache invalidation logic.
    """

    source_model: ClassVar[type[BrickSet]] = BrickSet

    id: int
    number: int
    production_status: str
    completeness: str
    has_instructions: bool
    has_box: bool
    is_factory_sealed: bool
    owner_initial_estimate: Optional[int]
    owner_id: int
    valuations: list[ValuationInlineDTO]
    valuations_count: int
    total_likes: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class OwnedBrickSetListItemDTO:
    """BrickSet item in `/users/me/bricksets` list.

    Adds `editable` derived rule evaluation flag (RB-01).
    """

    source_model: ClassVar[type[BrickSet]] = BrickSet

    id: int
    number: int
    production_status: str
    completeness: str
    valuations_count: int
    total_likes: int
    editable: bool  # derived from RB-01 rule logic
