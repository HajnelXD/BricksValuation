"""URL configuration for catalog app."""
from django.urls import path

from catalog.views.brickset_list import BrickSetListView
from catalog.views.brickset_detail_update import BrickSetDetailUpdateView

app_name = "catalog"
urlpatterns = [
    path("bricksets", BrickSetListView.as_view(), name="brickset-list"),
    # GET detail and PATCH update on same route (DRF handles methods)
    path(
        "bricksets/<int:pk>",
        BrickSetDetailUpdateView.as_view(),
        name="brickset-detail",
    ),
]
