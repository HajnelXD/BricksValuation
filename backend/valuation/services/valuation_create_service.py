"""Service implementing Valuation creation flow."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from catalog.exceptions import BrickSetNotFoundError
from catalog.models import BrickSet
from datastore.domains.valuation_dto import CreateValuationCommand, ValuationDTO
from valuation.exceptions import ValuationDuplicateError
from valuation.models import Valuation

User = get_user_model()


class CreateValuationService:
    """Coordinate the creation process for a new Valuation."""

    def execute(
        self,
        command: CreateValuationCommand,
        user: User,
    ) -> ValuationDTO:
        """Validate input, persist the new Valuation, and return DTO.

        Args:
            command: CreateValuationCommand with brickset_id, value, currency, comment
            user: Authenticated user creating the valuation (owner)

        Returns:
            ValuationDTO with created valuation data including timestamps

        Raises:
            BrickSetNotFoundError: If BrickSet with given id does not exist
            ValuationDuplicateError: If user already has valuation for this BrickSet
        """
        brickset = self._verify_brickset_exists(command.brickset_id)
        valuation = self._persist_valuation(command, user, brickset)

        return self._build_dto(valuation)

    def _verify_brickset_exists(self, brickset_id: int) -> BrickSet:
        """Verify that BrickSet with given id exists.

        Args:
            brickset_id: Primary key of BrickSet to verify

        Returns:
            BrickSet instance if found

        Raises:
            BrickSetNotFoundError: If BrickSet does not exist
        """
        try:
            return BrickSet.bricksets.get(pk=brickset_id)
        except BrickSet.DoesNotExist as exc:
            raise BrickSetNotFoundError(brickset_id) from exc

    def _persist_valuation(
        self,
        command: CreateValuationCommand,
        user: User,
        brickset: BrickSet,
    ) -> Valuation:
        """Build and persist Valuation to database within transaction.

        Catches IntegrityError for unique constraint violations.
        Other IntegrityError types (foreign key, check constraints) are re-raised.

        Args:
            command: CreateValuationCommand with value, currency, comment
            user: User creating the valuation
            brickset: BrickSet instance being valued

        Returns:
            Saved Valuation instance with id and timestamps

        Raises:
            ValuationDuplicateError: If uniqueness constraint is violated
            IntegrityError: For other integrity constraint violations
        """
        try:
            with transaction.atomic():
                # Use explicit user_id and brickset_id to avoid DRF proxy object issues
                # Use custom manager 'valuations' (not 'objects')
                valuation = Valuation.valuations.create(
                    user_id=user.id,
                    brickset_id=brickset.id,
                    value=command.value,
                    currency=command.currency or "PLN",
                    comment=command.comment,
                )

                return valuation
        except IntegrityError as exc:
            # Check which constraint was violated by examining error message
            error_message = str(exc).lower()
            if "valuation_unique_user_brickset" in error_message or "unique constraint" in error_message:
                raise ValuationDuplicateError("valuation_unique_user_brickset") from exc
            # Re-raise other integrity errors (foreign key, check constraints, etc.)
            raise

    @staticmethod
    def _build_dto(valuation: Valuation) -> ValuationDTO:
        """Map Valuation instance to DTO with all metadata.

        Args:
            valuation: Saved Valuation instance with id and timestamps

        Returns:
            ValuationDTO ready for API response
        """
        return ValuationDTO(
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
