"""API views for BrickSet detail endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.exceptions import BrickSetNotFoundError
from catalog.serializers.brickset_detail import BrickSetDetailSerializer
from catalog.services.brickset_detail_service import BrickSetDetailService


class BrickSetDetailView(GenericAPIView):  # noqa: WPS338
    """Handle GET /api/v1/bricksets/{id} detail endpoint."""

    permission_classes = [AllowAny]
    serializer_class = BrickSetDetailSerializer

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve full details of a BrickSet with valuations.

        Path parameters:
            - pk (int): BrickSet primary key

        Returns:
            Response: 200 OK with BrickSetDetailDTO
            - 404 Not Found: BrickSet with given id doesn't exist
            - 400 Bad Request: Invalid pk type (handled by DRF path converter)

        Response body (200 OK):
            {
                "id": 42,
                "number": 12345,
                "production_status": "RETIRED",
                "completeness": "COMPLETE",
                "has_instructions": true,
                "has_box": false,
                "is_factory_sealed": false,
                "owner_initial_estimate": null,
                "owner_id": 99,
                "valuations": [
                    {
                        "id": 101,
                        "user_id": 25,
                        "value": 450,
                        "currency": "PLN",
                        "comment": "Excellent condition",
                        "likes_count": 15,
                        "created_at": "2025-10-20T14:23:45.123Z"
                    }
                ],
                "valuations_count": 1,
                "total_likes": 15,
                "created_at": "2025-10-10T08:15:30.000Z",
                "updated_at": "2025-10-10T08:15:30.000Z"
            }

        Response body (404 Not Found):
            {
                "detail": "BrickSet with id 999 not found."
            }
        """
        service = BrickSetDetailService()

        try:
            brickset_dto = service.execute(pk)
        except BrickSetNotFoundError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize DTO and return 200 OK
        serializer = BrickSetDetailSerializer(brickset_dto)
        return Response(serializer.data, status=status.HTTP_200_OK)
