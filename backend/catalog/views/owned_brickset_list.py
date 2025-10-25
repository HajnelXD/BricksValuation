"""API view for listing owned bricksets for authenticated user."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.serializers.owned_brickset_list import OwnedBrickSetListItemSerializer
from catalog.services.owned_brickset_list_service import OwnedBrickSetListService


class OwnedBrickSetPagination(PageNumberPagination):
    """Custom pagination for owned BrickSet list endpoint."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class OwnedBrickSetListView(GenericAPIView):  # noqa: WPS338
    """Handle GET /api/v1/users/me/bricksets - list owned bricksets for auth user."""

    pagination_class = OwnedBrickSetPagination
    serializer_class = OwnedBrickSetListItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve paginated list of bricksets owned by authenticated user.

        Query parameters:
        - page (int): Page number (default 1)
        - page_size (int): Items per page (default 20, max 100)
        - ordering (string): Sort field (see ALLOWED_ORDERINGS for choices)
          Choices: created_at, -created_at, valuations_count, -valuations_count,
                   total_likes, -total_likes
          Default: -created_at (newest first)

        Returns:
            Response with paginated list of owned bricksets

        Response (200 OK):
            {
              "count": 15,
              "next": "http://api.example.com/api/v1/users/me/bricksets?page=2",
              "previous": null,
              "results": [
                {
                  "id": 42,
                  "number": 10001,
                  "production_status": "ACTIVE",
                  "completeness": "COMPLETE",
                  "valuations_count": 5,
                  "total_likes": 23,
                  "editable": true
                },
                ...
              ]
            }

        Errors:
            - 401 UNAUTHORIZED: Not authenticated (automatic via IsAuthenticated)
            - 400 BAD_REQUEST: Invalid ordering or pagination parameters
        """
        # Extract and validate ordering parameter
        ordering = request.query_params.get("ordering", None)

        # Get service and build QuerySet filtered by authenticated user
        service = OwnedBrickSetListService()
        queryset = service.get_queryset(request.user.id, ordering)

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Map QuerySet items to DTOs and serialize
            dtos = [service.map_to_dto(brickset) for brickset in page]
            return self.get_paginated_response(
                self.get_serializer(dtos, many=True).data,
            )

        # Fallback if no pagination (shouldn't happen with DRF pagination)
        dtos = [service.map_to_dto(brickset) for brickset in queryset]
        return Response(
            self.get_serializer(dtos, many=True).data,
            status=status.HTTP_200_OK,
        )
