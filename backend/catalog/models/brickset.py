"""BrickSet model.

Represents a unique LEGO set combination (FR-04..FR-05). Global uniqueness is
enforced across number, production status, completeness and condition flags.

ENUM fields are represented using Django TextChoices for portability. For
PostgreSQL we may later migrate to native ENUM types via a separate migration
using ``RunSQL`` for stricter typing (see db-plan).
"""

from __future__ import annotations

from django.conf import settings
from django.core import validators
from django.db import models


class ProductionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    RETIRED = "RETIRED", "Retired"


class Completeness(models.TextChoices):
    COMPLETE = "COMPLETE", "Complete"
    INCOMPLETE = "INCOMPLETE", "Incomplete"


MAX_SET_NUMBER = 9_999_999
MAX_INITIAL_ESTIMATE = 999_999
STATUS_LENGTH = 16
COMPLETENESS_LENGTH = 16


class BrickSetQuerySet(models.QuerySet):
    """Custom queryset for BrickSet convenience filters."""

    def complete(self) -> "BrickSetQuerySet":
        """Return only complete sets."""
        return self.filter(completeness=Completeness.COMPLETE)

    def incomplete(self) -> "BrickSetQuerySet":
        """Return only incomplete sets."""
        return self.filter(completeness=Completeness.INCOMPLETE)

    def with_box(self) -> "BrickSetQuerySet":
        """Sets that include original box."""
        return self.filter(has_box=True)

    def factory_sealed(self) -> "BrickSetQuerySet":
        """Sets that are factory sealed."""
        return self.filter(is_factory_sealed=True)


class BrickSet(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bricksets",
    )
    number = models.PositiveIntegerField(
        validators=[validators.MaxValueValidator(MAX_SET_NUMBER)],
        help_text="Set number (0-9,999,999).",
    )
    production_status = models.CharField(
        max_length=STATUS_LENGTH,
        choices=ProductionStatus.choices,
        help_text="Production status (ACTIVE/RETIRED).",
    )
    completeness = models.CharField(
        max_length=COMPLETENESS_LENGTH,
        choices=Completeness.choices,
        help_text="Completeness (COMPLETE/INCOMPLETE).",
    )
    has_instructions = models.BooleanField(default=False)
    has_box = models.BooleanField(default=False)
    is_factory_sealed = models.BooleanField(default=False)
    owner_initial_estimate = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(MAX_INITIAL_ESTIMATE),
        ],
        help_text="Optional initial owner estimate in PLN (1-999,999).",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = BrickSetQuerySet.as_manager()  # default manager
    bricksets = BrickSetQuerySet.as_manager()  # custom manager name (avoid WPS110)

    class Meta:
        verbose_name = "Brick Set"
        verbose_name_plural = "Brick Sets"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "number",
                    "production_status",
                    "completeness",
                    "has_instructions",
                    "has_box",
                    "is_factory_sealed",
                ),
                name="brickset_global_identity",
            ),
            models.CheckConstraint(
                check=models.Q(number__gte=0) & models.Q(number__lte=MAX_SET_NUMBER),
                name="brickset_number_range",
            ),
            models.CheckConstraint(
                check=(
                    (models.Q(owner_initial_estimate__isnull=True))
                    | (
                        models.Q(owner_initial_estimate__gt=0)
                        & models.Q(owner_initial_estimate__lt=MAX_INITIAL_ESTIMATE + 1)
                    )
                ),
                name="brickset_initial_estimate_range",
            ),
        ]
        indexes = [
            models.Index(fields=["number"], name="brickset_number_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Set #{self.number} ({self.get_completeness_display()})"
