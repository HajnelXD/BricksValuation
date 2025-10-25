"""URL configuration for catalog app."""
from django.urls import path

from catalog.views.brickset_list import BrickSetListView
from catalog.views.brickset_detail_update import BrickSetDetailUpdateView
from catalog.views.owned_brickset_list import OwnedBrickSetListView

app_name = "catalog"
urlpatterns = [
    path("bricksets", BrickSetListView.as_view(), name="brickset-list"),
    # GET detail and PATCH update on same route (DRF handles methods)
    path(
        "bricksets/<int:pk>",
        BrickSetDetailUpdateView.as_view(),
        name="brickset-detail",
    ),
    # GET owned bricksets for authenticated user
    path(
        "users/me/bricksets",
        OwnedBrickSetListView.as_view(),
        name="owned-brickset-list",
    ),
]
