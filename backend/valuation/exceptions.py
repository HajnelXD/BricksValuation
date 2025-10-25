"""Custom exceptions for valuation domain operations."""
from __future__ import annotations

from collections.abc import Mapping


class ValuationValidationError(Exception):
    """Raised when Valuation data fails model validation before persistence."""

    def __init__(self, errors: Mapping[str, list[str]]) -> None:
        super().__init__("Invalid Valuation data.")
        self.errors = errors


class ValuationDuplicateError(Exception):
    """Raised when Valuation violates uniqueness constraint.

    Occurs when user attempts to create second valuation for same BrickSet.
    """

    def __init__(self, constraint: str = "valuation_unique_user_brickset") -> None:
        super().__init__("Valuation for this BrickSet already exists.")
        self.constraint = constraint
        self.message = "Valuation for this BrickSet already exists."


class ValuationNotFoundError(Exception):
    """Raised when Valuation with given id does not exist."""

    def __init__(self, valuation_id: int) -> None:
        super().__init__(f"Valuation with id {valuation_id} not found.")
        self.valuation_id = valuation_id
        self.message = f"Valuation with id {valuation_id} not found."
