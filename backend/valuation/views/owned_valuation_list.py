"""API view for listing owned valuations for authenticated user."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from valuation.serializers.owned_valuation_list import OwnedValuationListItemSerializer
from valuation.services.owned_valuation_list_service import OwnedValuationListService


class OwnedValuationPagination(PageNumberPagination):
    """Custom pagination for owned Valuation list endpoint."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class OwnedValuationListView(GenericAPIView):
    """Handle GET /api/v1/users/me/valuations - list owned valuations for auth user."""

    pagination_class = OwnedValuationPagination
    serializer_class = OwnedValuationListItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Retrieve paginated list of valuations owned by authenticated user.

        Query parameters:
        - page (int): Page number (default 1)
        - page_size (int): Items per page (default 20, max 100)
        - ordering (string): Sort field (see ALLOWED_ORDERINGS for choices)
          Choices: created_at, -created_at, likes_count, -likes_count,
                   value, -value
          Default: -created_at (newest first)

        Returns:
            Response with paginated list of owned valuations

        Response (200 OK):
            {
              "count": 7,
              "next": "http://api.example.com/api/v1/users/me/valuations?page=2",
              "previous": null,
              "results": [
                {
                  "id": 77,
                  "brickset": {
                    "id": 10,
                    "number": 12345
                  },
                  "value": 400,
                  "currency": "PLN",
                  "likes_count": 9,
                  "created_at": "2025-10-20T14:30:00Z"
                },
                ...
              ]
            }

        Errors:
            - 401 UNAUTHORIZED: Not authenticated (automatic via IsAuthenticated)
            - 400 BAD_REQUEST: Invalid ordering or pagination parameters
        """
        # Extract ordering parameter
        ordering = request.query_params.get("ordering", None)

        # Get service and build QuerySet filtered by authenticated user
        service = OwnedValuationListService()
        queryset = service.get_queryset(request.user.id, ordering)

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Map QuerySet items to DTOs and serialize
            dtos = [service.map_to_dto(valuation) for valuation in page]
            return self.get_paginated_response(
                self.get_serializer(dtos, many=True).data,
            )

        # Fallback if no pagination (shouldn't happen with DRF pagination)
        dtos = [service.map_to_dto(valuation) for valuation in queryset]
        return Response(
            self.get_serializer(dtos, many=True).data,
            status=status.HTTP_200_OK,
        )
