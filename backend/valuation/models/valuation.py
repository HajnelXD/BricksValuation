"""Valuation model definition.

Represents a user's valuation of a BrickSet (FR-10..FR-11). One valuation per
user-set pair (unique constraint). ``likes_count`` is denormalized for fast
ordering and will be maintained by signals (or DB triggers later) (FR-12).
"""

from __future__ import annotations

from django.conf import settings
from django.core import validators
from django.db import models

from catalog.models import BrickSet


class ValuationQuerySet(models.QuerySet):
    def popular(self) -> "ValuationQuerySet":
        return self.filter(likes_count__gt=0).order_by("-likes_count")

    def for_user(self, user) -> "ValuationQuerySet":  # type: ignore[override]
        return self.filter(user=user)


MAX_VALUATION = 999_999


class Valuation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="valuations",
    )
    brickset = models.ForeignKey(
        BrickSet,
        on_delete=models.CASCADE,
        related_name="valuations",
    )
    value = models.PositiveIntegerField(  # noqa: WPS110 (domain term)
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(MAX_VALUATION),
        ],
        help_text="Valuation value in PLN (1-999,999).",
    )
    currency = models.CharField(max_length=3, default="PLN")
    comment = models.TextField(null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0, help_text="Denormalized likes count >=0.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    valuations = ValuationQuerySet.as_manager()  # custom manager name

    class Meta:
        verbose_name = "Valuation"
        verbose_name_plural = "Valuations"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "brickset"), name="valuation_unique_user_brickset"
            ),
            models.CheckConstraint(
                check=(models.Q(value__gt=0) & models.Q(value__lte=MAX_VALUATION)),  # noqa: WPS514
                name="valuation_value_range",
            ),
            models.CheckConstraint(
                check=models.Q(likes_count__gte=0),
                name="valuation_likes_nonnegative",
            ),
        ]
        indexes = [
            models.Index(fields=["brickset"], name="valuation_brickset_idx"),
            models.Index(fields=["user"], name="valuation_user_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Valuation {self.value} {self.currency} by {self.user_id} for set {self.brickset_id}"
