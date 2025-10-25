"""API views for BrickSet update (PATCH) endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.exceptions import BrickSetNotFoundError, BrickSetEditForbiddenError
from catalog.serializers.brickset_update import UpdateBrickSetSerializer
from catalog.serializers.brickset_detail import BrickSetDetailSerializer
from catalog.services.brickset_update_service import UpdateBrickSetService


class BrickSetUpdateView(GenericAPIView):  # noqa: WPS338
    """Handle PATCH /api/v1/bricksets/{id} update endpoint."""

    permission_classes = [IsAuthenticated]
    serializer_class = UpdateBrickSetSerializer

    def patch(self, request: Request, pk: int) -> Response:
        """Update BrickSet fields (partial update) with authorization checks.

        Endpoint applies partial update to allowed fields
        (has_box, owner_initial_estimate). Requires authentication.
        Only owner can edit. RB-01 business rules enforced:
        - Edit forbidden if other users' valuations exist
        - Edit forbidden if owner's valuation has likes > 0

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

        Response body (200 OK):
            {
                "id": 42,
                "number": 12345,
                "production_status": "RETIRED",
                "completeness": "COMPLETE",
                "has_instructions": true,
                "has_box": false,  # UPDATED
                "is_factory_sealed": false,
                "owner_initial_estimate": 450,  # UPDATED
                "owner_id": 99,
                "valuations": [...],
                "valuations_count": 1,
                "total_likes": 15,
                "created_at": "2025-10-10T08:15:30.000Z",
                "updated_at": "2025-10-25T11:42:00.000Z"  # UPDATED
            }

        Response body (400 Bad Request - validation error):
            {
                "has_box": ["Must be a valid boolean."],
                "owner_initial_estimate": [
                    "Ensure this value is less than or equal to 999999."
                ]
            }
            or
            {
                "non_field_errors": [
                    "At least one field must be provided for update."
                ]
            }

        Response body (403 Forbidden - not owner):
            {
                "detail": "Only the owner can edit this BrickSet.",
                "reason": "not_owner"
            }

        Response body (403 Forbidden - RB-01 violation):
            {
                "detail": (
                    "BrickSet cannot be edited. Valuations from other users "
                    "exist or owner's valuation has likes."
                ),
                "reason": "other_users_valuations_exist"
                # or "owner_valuation_has_likes"
            }

        Response body (404 Not Found):
            {
                "detail": "BrickSet with id 999 not found."
            }
        """
        # Validate and deserialize request data
        serializer = UpdateBrickSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Convert to command object
        command = serializer.to_command()

        # Execute update service with authorization and business logic
        service = UpdateBrickSetService()
        try:
            brickset_dto = service.execute(pk, command, request.user)
        except BrickSetNotFoundError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except BrickSetEditForbiddenError as exc:
            # Include reason field for diagnostics/frontend logic
            return Response(
                {
                    "detail": exc.message,
                    "reason": exc.reason,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Serialize updated DTO and return 200 OK
        response_serializer = BrickSetDetailSerializer(brickset_dto)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
