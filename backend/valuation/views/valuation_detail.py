"""API views for Valuation detail endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from valuation.exceptions import ValuationNotFoundError
from valuation.serializers.valuation_detail import ValuationSerializer
from valuation.services.valuation_detail_service import ValuationDetailService


class ValuationDetailView(GenericAPIView):  # noqa: WPS338
    """Handle GET /api/v1/valuations/{id} detail endpoint."""

    permission_classes = [IsAuthenticated]
    serializer_class = ValuationSerializer

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve full details of a single Valuation by id.

        Path parameters:
            - pk (int): Valuation primary key

        Returns:
            Response: 200 OK with ValuationDetailDTO
            - 401 Unauthorized: User not authenticated
            - 404 Not Found: Valuation with given id doesn't exist
            - 400 Bad Request: Invalid pk type (handled by DRF path converter)

        Response body (200 OK):
            {
                "id": 77,
                "brickset_id": 10,
                "user_id": 99,
                "value": 400,
                "currency": "PLN",
                "comment": "Looks complete and in great condition",
                "likes_count": 9,
                "created_at": "2025-10-25T11:42:00.000Z",
                "updated_at": "2025-10-25T11:42:00.000Z"
            }

        Response body (404 Not Found):
            {
                "detail": "Valuation with id 999 not found."
            }

        Response body (401 Unauthorized):
            {
                "detail": "Authentication credentials were not provided."
            }
        """
        service = ValuationDetailService()

        try:
            valuation_dto = service.execute(pk)
        except ValuationNotFoundError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize DTO and return 200 OK
        serializer = ValuationSerializer(valuation_dto)
        return Response(serializer.data, status=status.HTTP_200_OK)
