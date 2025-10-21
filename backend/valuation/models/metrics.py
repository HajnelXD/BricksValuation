"""SystemMetrics (valuation_metrics) singleton table.

Stores aggregated metrics for analytics (FR-19). Only a single row (id=1) is
expected; application code can enforce creation and updates. Future: triggers
in PostgreSQL for automatic refresh.
"""

from __future__ import annotations

from django.db import models


class SystemMetrics(models.Model):
    total_sets = models.PositiveIntegerField(default=0)
    serviced_sets = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Metrics"
        verbose_name_plural = "System Metrics"
        db_table = "valuation_metrics"  # Align table name with plan

    def __str__(self) -> str:  # pragma: no cover - trivial
        return "System Metrics Singleton"
