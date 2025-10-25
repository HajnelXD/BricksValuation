"""API views for BrickSet creation endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.exceptions import BrickSetDuplicateError, BrickSetValidationError
from catalog.serializers.brickset_create import CreateBrickSetSerializer
from catalog.serializers.brickset_list import BrickSetListItemSerializer
from catalog.services.brickset_create_service import CreateBrickSetService


class CreateBrickSetView(APIView):
    """Handle BrickSet creation via POST /api/v1/bricksets."""

    permission_classes = [IsAuthenticated]
    service_class = CreateBrickSetService

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
        service = self.service_class()
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
