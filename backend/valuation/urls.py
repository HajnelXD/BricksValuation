"""URL configuration for valuation app."""
from django.urls import path

from valuation.views.brickset_valuations import BrickSetValuationsView
from valuation.views.valuation_detail import ValuationDetailView
from valuation.views.valuation_like import ValuationLikeView

app_name = "valuation"
urlpatterns = [
    path(
        "bricksets/<int:brickset_id>/valuations",
        BrickSetValuationsView.as_view(),
        name="brickset-valuations",
    ),
    path(
        "valuations/<int:pk>",
        ValuationDetailView.as_view(),
        name="valuation-detail",
    ),
    path(
        "valuations/<int:valuation_id>/likes",
        ValuationLikeView.as_view(),
        name="valuation-like",
    ),
]
