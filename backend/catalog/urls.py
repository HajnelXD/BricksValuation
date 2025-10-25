"""URL configuration for catalog app."""
from django.urls import path

from catalog.views.brickset_list import BrickSetListView
from catalog.views.brickset_detail import BrickSetDetailView

app_name = "catalog"
urlpatterns = [
    path("bricksets", BrickSetListView.as_view(), name="brickset-list"),  # GET + POST
    path("bricksets/<int:pk>", BrickSetDetailView.as_view(), name="brickset-detail"),  # GET detail
]
