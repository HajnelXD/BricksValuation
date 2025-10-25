"""URL configuration for valuation app."""
from django.urls import path

from valuation.views.brickset_valuations import BrickSetValuationsView
from valuation.views.owned_valuation_list import OwnedValuationListView
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
    # GET owned valuations for authenticated user
    path(
        "users/me/valuations",
        OwnedValuationListView.as_view(),
        name="owned-valuation-list",
    ),
]
