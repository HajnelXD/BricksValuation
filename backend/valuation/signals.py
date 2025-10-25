"""Django signals for valuation app.

Maintains denormalized counters (``likes_count`` on Valuation) and provides
placeholders for future SystemMetrics refresh logic that will later be moved
to PostgreSQL triggers for better atomicity and performance.
"""

from __future__ import annotations

from django.db import models
from django.dispatch import receiver

from .models import Like, Valuation, SystemMetrics  # noqa: WPS300


def _touch_metrics() -> None:
    """Refresh metrics singleton (simplified full recompute).

    This approach executes aggregate queries each time; acceptable for MVP.
    In future we will optimize incrementally or move logic to DB triggers.
    """
    try:
        metrics = SystemMetrics.objects.get(pk=1)
    except SystemMetrics.DoesNotExist:  # pragma: no cover - creation path
        metrics = SystemMetrics.objects.create(pk=1)

    from catalog.models import BrickSet  # local import to avoid circular at load

    # total_sets
    metrics.total_sets = BrickSet.objects.count()

    # active_users: users with at least one brickset or valuation
    from django.contrib.auth import get_user_model

    User = get_user_model()
    metrics.active_users = (
        User.objects.filter(
            models.Q(bricksets__isnull=False) | models.Q(valuations__isnull=False),
        ).distinct()
        .count()
    )

    # serviced_sets definition per db-plan using EXISTS subqueries
    val_not_owner = (
        Valuation.valuations.filter(brickset_id=models.OuterRef("pk"))
        .exclude(user_id=models.F("brickset__owner_id"))
    )
    val_owner_liked = Valuation.valuations.filter(
        brickset_id=models.OuterRef("pk"), user_id=models.F("brickset__owner_id"), likes_count__gt=0
    )
    metrics.serviced_sets = (
        BrickSet.objects.annotate(
            has_external=models.Exists(val_not_owner), has_owner_liked=models.Exists(val_owner_liked)
        ).filter(models.Q(has_external=True) | models.Q(has_owner_liked=True))
        .count()
    )
    metrics.save(update_fields=["total_sets", "active_users", "serviced_sets", "updated_at"])


@receiver(models.signals.post_save, sender=Like)
def increment_likes_count(sender, instance: Like, created: bool, **kwargs) -> None:
    if not created:
        return
    Valuation.valuations.filter(pk=instance.valuation_id).update(
        likes_count=models.F("likes_count") + 1,
    )
    _touch_metrics()


@receiver(models.signals.post_delete,  sender=Like)
def decrement_likes_count(sender, instance: Like, **kwargs) -> None:
    Valuation.valuations.filter(pk=instance.valuation_id).update(
        likes_count=models.Case(
            models.When(likes_count__gt=0, then=models.F("likes_count") - 1),
            default=models.F("likes_count"),
            output_field=models.PositiveIntegerField(),
        ),
    )
    _touch_metrics()
