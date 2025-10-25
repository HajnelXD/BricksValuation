"""Service implementing BrickSet creation flow."""
from __future__ import annotations

from django.db import IntegrityError, transaction

from catalog.exceptions import BrickSetDuplicateError
from catalog.models import BrickSet
from datastore.domains.catalog_dto import (
    CreateBrickSetCommand,
    BrickSetListItemDTO,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateBrickSetService:
    """Coordinate the creation process for a new BrickSet."""

    def execute(self, command: CreateBrickSetCommand, owner: User) -> BrickSetListItemDTO:
        """Validate input, persist the new BrickSet, and return list item DTO.

        Note: Field-level validation is done by the serializer before the command
        is passed here. We only handle database-level constraints (IntegrityError
        for uniqueness violations).
        """
        brickset = self._build_brickset(command, owner)
        self._persist_brickset(brickset)

        return self._build_dto(brickset)

    def _build_brickset(self, command: CreateBrickSetCommand, owner: User) -> BrickSet:
        """Construct BrickSet instance from command and owner."""
        return BrickSet(
            owner=owner,
            number=command.number,
            production_status=command.production_status,
            completeness=command.completeness,
            has_instructions=command.has_instructions,
            has_box=command.has_box,
            is_factory_sealed=command.is_factory_sealed,
            owner_initial_estimate=command.owner_initial_estimate,
        )

    def _persist_brickset(self, brickset: BrickSet) -> None:
        """Persist BrickSet to database within transaction.

        Catches IntegrityError for unique constraint violations.
        """
        try:
            with transaction.atomic():
                brickset.save()
        except IntegrityError as exc:
            raise BrickSetDuplicateError("brickset_global_identity") from exc

    @staticmethod
    def _build_dto(brickset: BrickSet) -> BrickSetListItemDTO:
        """Map BrickSet instance to list item DTO with initial values."""
        return BrickSetListItemDTO(
            id=brickset.id,
            number=brickset.number,
            production_status=brickset.production_status,
            completeness=brickset.completeness,
            has_instructions=brickset.has_instructions,
            has_box=brickset.has_box,
            is_factory_sealed=brickset.is_factory_sealed,
            owner_id=brickset.owner_id,
            owner_initial_estimate=brickset.owner_initial_estimate,
            valuations_count=0,
            total_likes=0,
            top_valuation=None,
        )
