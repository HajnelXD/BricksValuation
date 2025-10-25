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


class LikeOwnValuationError(Exception):
    """Raised when user attempts to like their own Valuation."""

    def __init__(self, valuation_id: int) -> None:
        super().__init__("Cannot like your own valuation.")
        self.valuation_id = valuation_id
        self.message = "Cannot like your own valuation."


class LikeDuplicateError(Exception):
    """Raised when Like violates uniqueness constraint.

    Occurs when user attempts to like same Valuation twice (unique on user+valuation).
    """

    def __init__(self, valuation_id: int, user_id: int) -> None:
        super().__init__(
            f"Like for valuation {valuation_id} by user {user_id} already exists."
        )
        self.valuation_id = valuation_id
        self.user_id = user_id
        self.message = (
            f"Like for valuation {valuation_id} by user {user_id} already exists."
        )


class LikeNotFoundError(Exception):
    """Raised when Like with given valuation_id and user_id does not exist.

    Occurs when user attempts to unlike a valuation they haven't liked or
    the like has already been removed.
    """

    def __init__(self, valuation_id: int, user_id: int) -> None:
        super().__init__(
            f"Like for valuation {valuation_id} by user {user_id} not found."
        )
        self.valuation_id = valuation_id
        self.user_id = user_id
        self.message = (
            f"Like for valuation {valuation_id} by user {user_id} not found."
        )
