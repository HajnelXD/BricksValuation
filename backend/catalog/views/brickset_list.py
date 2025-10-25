"""API views for catalog endpoints."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.exceptions import BrickSetDuplicateError, BrickSetValidationError
from catalog.serializers.brickset_create import CreateBrickSetSerializer
from catalog.serializers.brickset_list import (
    BrickSetFilterSerializer,
    BrickSetListItemSerializer,
)
from catalog.services.brickset_create_service import CreateBrickSetService
from catalog.services.brickset_list_service import BrickSetListService


class BrickSetPagination(PageNumberPagination):
    """Custom pagination for BrickSet list endpoint."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BrickSetListView(GenericAPIView):  # noqa: WPS338
    """Handle GET /api/v1/bricksets list and POST /api/v1/bricksets create."""

    pagination_class = BrickSetPagination
    serializer_class = BrickSetListItemSerializer

    def get_permissions(self):
        """Return different permissions for GET vs POST."""
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request) -> Response:
        """Retrieve paginated list of bricksets with optional filters.

        Query parameters:
        - page (int): Page number (default 1)
        - page_size (int): Items per page (default 20, max 100)
        - q (string): Search by set number
        - production_status (ACTIVE|RETIRED): Filter by status
        - completeness (COMPLETE|INCOMPLETE): Filter by completeness
        - has_instructions (bool): Filter by instructions
        - has_box (bool): Filter by box
        - is_factory_sealed (bool): Filter by seal
        - ordering (string): Sort field (see FilterSerializer for choices)

        Returns:
            Response with paginated list of bricksets
        """
        # Validate query parameters
        filter_serializer = BrickSetFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # Get filtered and annotated QuerySet from service
        service = BrickSetListService()
        queryset = service.get_queryset(filter_serializer.to_filter_dict())

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
        return Response(self.get_serializer(dtos, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Create a new BrickSet for authenticated user.

        Request body (JSON):
            - number (int): Set number (0-9,999,999) [required]
            - production_status (str): ACTIVE|RETIRED [required]
            - completeness (str): COMPLETE|INCOMPLETE [required]
            - has_instructions (bool): [required]
            - has_box (bool): [required]
            - is_factory_sealed (bool): [required]
            - owner_initial_estimate (int): 1-999,999 [optional]

        Returns:
            Response: 201 Created with BrickSetListItemDTO
            - 400 Bad Request: Validation error
            - 409 Conflict: Duplicate BrickSet
            - 401 Unauthorized: Not authenticated
        """
        # Validate and deserialize request data
        serializer = CreateBrickSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Convert validated data to command object
        command = serializer.to_command()

        # Execute service layer with authenticated user as owner
        service = CreateBrickSetService()
        try:
            brickset_dto = service.execute(command, request.user)
        except BrickSetValidationError as exc:
            return Response(
                {"errors": exc.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BrickSetDuplicateError as exc:
            return Response(
                {
                    "detail": exc.message,
                    "constraint": exc.constraint,
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Serialize DTO and return as 201 response
        response_serializer = BrickSetListItemSerializer(brickset_dto)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
