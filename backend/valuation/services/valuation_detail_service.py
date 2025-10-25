"""Service implementing Valuation detail retrieval."""
from __future__ import annotations

from datastore.domains.valuation_dto import ValuationDetailDTO
from valuation.exceptions import ValuationNotFoundError
from valuation.models import Valuation


class ValuationDetailService:  # noqa: WPS338
    """Coordinate Valuation detail retrieval and mapping to DTO."""

    def execute(self, valuation_id: int) -> ValuationDetailDTO:
        """Fetch Valuation by id and return as ValuationDetailDTO.

        Flow:
        1. Fetch Valuation by id (primary key lookup)
        2. If not found -> raise ValuationNotFoundError
        3. Map Valuation instance to ValuationDetailDTO
        4. Return DTO with all fields including updated_at

        Args:
            valuation_id: Primary key of the Valuation

        Returns:
            ValuationDetailDTO with all fields populated including updated_at

        Raises:
            ValuationNotFoundError: If Valuation with given id doesn't exist
        """
        try:
            valuation = Valuation.valuations.get(pk=valuation_id)
        except Valuation.DoesNotExist as exc:
            raise ValuationNotFoundError(valuation_id) from exc

        return self._build_dto(valuation)

    def _build_dto(self, valuation: Valuation) -> ValuationDetailDTO:
        """Map Valuation model instance to ValuationDetailDTO.

        Args:
            valuation: Valuation model instance

        Returns:
            ValuationDetailDTO with all fields from the model
        """
        return ValuationDetailDTO(
            id=valuation.id,
            brickset_id=valuation.brickset_id,
            user_id=valuation.user_id,
            value=valuation.value,
            currency=valuation.currency,
            comment=valuation.comment,
            likes_count=valuation.likes_count,
            created_at=valuation.created_at,
            updated_at=valuation.updated_at,
        )
