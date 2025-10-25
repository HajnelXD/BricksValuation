"""URL configuration for catalog app."""
from django.urls import path

from catalog.views.brickset_list import BrickSetListView

app_name = "catalog"
urlpatterns = [
    path("bricksets", BrickSetListView.as_view(), name="brickset-list"),  # GET + POST
]
