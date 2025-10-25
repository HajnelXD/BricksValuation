"""API views for Like endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from datastore.domains.valuation_dto import CreateLikeCommand
from valuation.exceptions import (
    LikeDuplicateError,
    LikeOwnValuationError,
    ValuationNotFoundError,
)
from valuation.serializers.like import LikeSerializer
from valuation.services.like_valuation_service import LikeValuationService


class ValuationLikeView(GenericAPIView):  # noqa: WPS338
    """Handle POST /api/v1/valuations/{valuation_id}/likes endpoint."""

    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def post(self, request: Request, valuation_id: int) -> Response:
        """Create a new Like for authenticated user on a Valuation.

        Path parameter:
            - valuation_id (int): Valuation identifier [required]

        Request body:
            - Empty JSON object {} (no fields required)

        Returns:
            Response: 201 Created with LikeDTO
            - 401 Unauthorized: Not authenticated
            - 403 Forbidden: User attempts to like their own valuation
            - 404 Not Found: Valuation with given id doesn't exist
            - 409 Conflict: User already liked this valuation

        Response body (201 Created):
            {
                "valuation_id": 77,
                "user_id": 42,
                "created_at": "2025-10-25T12:30:00.000Z"
            }

        Response body (403 Forbidden - own valuation):
            {
                "detail": "Cannot like your own valuation."
            }

        Response body (404 Not Found):
            {
                "detail": "Valuation with id 999 not found."
            }

        Response body (409 Conflict - duplicate):
            {
                "detail": "Like for valuation 77 by user 42 already exists."
            }

        Response body (401 Unauthorized):
            {
                "detail": "Authentication credentials were not provided."
            }
        """
        # Create command with path parameter and authenticated user
        command = CreateLikeCommand(
            valuation_id=valuation_id,
            user_id=request.user.id,
        )

        # Execute service layer
        service = LikeValuationService()
        try:
            like_dto = service.execute(command)
        except ValuationNotFoundError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LikeOwnValuationError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_403_FORBIDDEN,
            )
        except LikeDuplicateError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_409_CONFLICT,
            )

        # Serialize DTO and return as 201 response
        serializer = LikeSerializer(like_dto)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
