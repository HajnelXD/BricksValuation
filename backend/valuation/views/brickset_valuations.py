"""API views for valuation endpoints."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.exceptions import BrickSetNotFoundError
from valuation.exceptions import ValuationDuplicateError
from valuation.serializers.valuation_create import CreateValuationSerializer
from valuation.serializers.valuation_detail import ValuationSerializer
from valuation.services.valuation_create_service import CreateValuationService


class BrickSetValuationsView(GenericAPIView):
    """Handle POST /api/v1/bricksets/{brickset_id}/valuations create."""

    permission_classes = [IsAuthenticated]
    serializer_class = ValuationSerializer

    def post(self, request: Request, brickset_id: int) -> Response:
        """Create a new Valuation for authenticated user on a BrickSet.

        Path parameter:
            - brickset_id (int): BrickSet identifier [required]

        Request body (JSON):
            - value (int): Valuation value (1-999,999) [required]
            - currency (str): Currency code (max 3 chars, default 'PLN') [optional]
            - comment (str): Optional comment [optional]

        Returns:
            Response: 201 Created with ValuationDTO
            - 400 Bad Request: Validation error (invalid field values)
            - 401 Unauthorized: Not authenticated
            - 404 Not Found: BrickSet does not exist
            - 409 Conflict: User already has valuation for this BrickSet

        Raises:
            Handled exceptions:
            - BrickSetNotFoundError: Returns 404
            - ValuationDuplicateError: Returns 409
            - ValidationError (from DRF): Returns 400 automatically
        """
        # Validate and deserialize request data
        serializer = CreateValuationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Convert validated data to command object with path parameter
        command = serializer.to_command(brickset_id)

        # Execute service layer with authenticated user
        service = CreateValuationService()
        try:
            valuation_dto = service.execute(command, request.user)
        except BrickSetNotFoundError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValuationDuplicateError as exc:
            return Response(
                {
                    "detail": exc.message,
                    "constraint": exc.constraint,
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Serialize DTO and return as 201 response
        response_serializer = ValuationSerializer(valuation_dto)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
