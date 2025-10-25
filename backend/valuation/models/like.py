"""Like model.

Represents a user's like on a valuation (FR-12..FR-13). Application layer will
prevent liking one's own valuation; optional DB trigger may be added later.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from .valuation import Valuation  # noqa: WPS300


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="valuation_likes",
    )
    valuation = models.ForeignKey(
        Valuation,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "valuation"), name="like_unique_user_valuation"
            ),
        ]
        indexes = [
            models.Index(fields=["valuation"], name="like_valuation_idx"),
            models.Index(fields=["user"], name="like_user_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Like by {self.user_id} on valuation {self.valuation_id}"
