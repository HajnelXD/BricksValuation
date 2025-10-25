"""Custom exceptions for catalog domain operations."""
from __future__ import annotations

from collections.abc import Mapping


class BrickSetValidationError(Exception):
    """Raised when BrickSet data fails model validation before persistence."""

    def __init__(self, errors: Mapping[str, list[str]]) -> None:
        super().__init__("Invalid BrickSet data.")
        self.errors = errors


class BrickSetDuplicateError(Exception):
    """Raised when BrickSet violates global uniqueness constraint."""

    def __init__(self, constraint: str = "brickset_global_identity") -> None:
        super().__init__("BrickSet with this combination already exists.")
        self.constraint = constraint
        self.message = "BrickSet with this combination already exists."
