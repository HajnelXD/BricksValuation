"""URL configuration for valuation app."""
from django.urls import path

from valuation.views.brickset_valuations import BrickSetValuationsView

app_name = "valuation"
urlpatterns = [
    path(
        "bricksets/<int:brickset_id>/valuations",
        BrickSetValuationsView.as_view(),
        name="brickset-valuations",
    ),
]
