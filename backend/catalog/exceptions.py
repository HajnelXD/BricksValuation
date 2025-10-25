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


class BrickSetNotFoundError(Exception):
    """Raised when BrickSet with given id does not exist."""

    def __init__(self, brickset_id: int) -> None:
        super().__init__(f"BrickSet with id {brickset_id} not found.")
        self.brickset_id = brickset_id
        self.message = f"BrickSet with id {brickset_id} not found."


class BrickSetEditForbiddenError(Exception):
    """Raised when BrickSet edit violates business rules (RB-01) or authorization.

    Error reasons:
    - "not_owner": Requesting user is not the BrickSet owner
    - "other_users_valuations_exist": Valuations from other users prevent edit (RB-01)
    - "owner_valuation_has_likes": Owner's valuation has likes > 0 (RB-01)
    """

    def __init__(self, reason: str) -> None:
        """Initialize with reason code for diagnostics.

        Args:
            reason: One of "not_owner", "other_users_valuations_exist",
                   "owner_valuation_has_likes"
        """
        self.reason = reason

        # Map reason to user-facing message
        messages = {
            "not_owner": "Only the owner can edit this BrickSet.",
            "other_users_valuations_exist": (
                "BrickSet cannot be edited. Valuations from other users exist "
                "or owner's valuation has likes."
            ),
            "owner_valuation_has_likes": (
                "BrickSet cannot be edited. Valuations from other users exist "
                "or owner's valuation has likes."
            ),
        }
        self.message = messages.get(reason, "BrickSet edit forbidden.")
        super().__init__(self.message)
