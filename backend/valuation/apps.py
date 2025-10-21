from django.apps import AppConfig


class ValuationConfig(AppConfig):
    name = "valuation"
    verbose_name = "Valuation"

    def ready(self) -> None:  # pragma: no cover - side-effect import
        # Import signal handlers.
        from . import signals  # noqa: F401, WPS300
