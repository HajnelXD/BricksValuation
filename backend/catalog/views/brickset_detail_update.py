"""API views for BrickSet detail and update endpoints."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.exceptions import BrickSetNotFoundError, BrickSetEditForbiddenError
from catalog.serializers.brickset_detail import BrickSetDetailSerializer
from catalog.serializers.brickset_update import UpdateBrickSetSerializer
from catalog.services.brickset_detail_service import BrickSetDetailService
from catalog.services.brickset_update_service import UpdateBrickSetService


_DETAIL_KEY = "detail"
_AUTH_ERROR_MSG = "Authentication credentials were not provided."


class BrickSetDetailUpdateView(GenericAPIView):  # noqa: WPS338
    """Handle GET and PATCH /api/v1/bricksets/{id} endpoints."""

    permission_classes = [AllowAny]
    serializer_class = BrickSetDetailSerializer

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve full details of a BrickSet with valuations.

        Path parameters:
            - pk (int): BrickSet primary key

        Returns:
            Response: 200 OK with BrickSetDetailDTO
            - 404 Not Found: BrickSet with given id doesn't exist
        """
        service = BrickSetDetailService()

        try:
            brickset_dto = service.execute(pk)
        except BrickSetNotFoundError as exc:
            return Response(
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BrickSetDetailSerializer(brickset_dto)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pk: int) -> Response:
        """Update BrickSet fields (partial update).

        Requires authentication. Only owner can edit.

        Path parameters:
            - pk (int): BrickSet primary key

        Request body (JSON, all fields optional but at least one required):
            {
                "has_box": false,
                "owner_initial_estimate": 450
            }

        Returns:
            Response: 200 OK with updated BrickSetDetailDTO
            - 400 Bad Request: Validation error
            - 401 Unauthorized: Not authenticated
            - 403 Forbidden: Not owner or RB-01 rule violation
            - 404 Not Found: BrickSet with given id doesn't exist
        """
        # Check authentication
        if not request.user or not request.user.is_authenticated:
            return Response(
                {_DETAIL_KEY: _AUTH_ERROR_MSG},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Validate and deserialize request data
        serializer = UpdateBrickSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        command = serializer.to_command()

        # Execute update service with authorization and business logic
        service = UpdateBrickSetService()
        try:
            brickset_dto = service.execute(pk, command, request.user)
        except BrickSetNotFoundError as exc:
            return Response(
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except BrickSetEditForbiddenError as exc:
            return Response(
                {
                    _DETAIL_KEY: exc.message,
                    "reason": exc.reason,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # Serialize updated DTO and return 200 OK
        response_serializer = BrickSetDetailSerializer(brickset_dto)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
