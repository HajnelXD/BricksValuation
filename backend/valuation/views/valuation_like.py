"""API views for Like endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from datastore.domains.valuation_dto import CreateLikeCommand, UnlikeValuationCommand
from valuation.exceptions import (
    LikeDuplicateError,
    LikeNotFoundError,
    LikeOwnValuationError,
    ValuationNotFoundError,
)
from valuation.serializers.like import LikeSerializer
from valuation.services.like_valuation_service import LikeValuationService
from valuation.services.unlike_valuation_service import UnlikeValuationService


_DETAIL_KEY = "detail"


class ValuationLikeView(GenericAPIView):  # noqa: WPS338
    """Handle POST and DELETE /api/v1/valuations/{valuation_id}/likes endpoint."""

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
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LikeOwnValuationError as exc:
            return Response(
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_403_FORBIDDEN,
            )
        except LikeDuplicateError as exc:
            return Response(
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_409_CONFLICT,
            )

        # Serialize DTO and return as 201 response
        serializer = LikeSerializer(like_dto)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, valuation_id: int) -> Response:
        """Delete a Like from authenticated user on a Valuation.

        Requires authentication. Only the user who created the like can delete it.

        Path parameter:
            - valuation_id (int): Valuation identifier [required]

        Request body:
            - Empty (no body required)

        Returns:
            Response: 204 No Content (no response body)
            - 401 Unauthorized: Not authenticated
            - 404 Not Found: Like does not exist for this (valuation, user) pair

        Response body (204 No Content):
            (empty - no body)

        Response body (404 Not Found):
            {
                "detail": "Like for valuation 77 by user 42 not found."
            }

        Response body (401 Unauthorized):
            {
                "detail": "Authentication credentials were not provided."
            }
        """
        # Create command with path parameter and authenticated user
        command = UnlikeValuationCommand(
            valuation_id=valuation_id,
            user_id=request.user.id,
        )

        # Execute service layer
        service = UnlikeValuationService()
        try:
            service.execute(command)
        except LikeNotFoundError as exc:
            return Response(
                {_DETAIL_KEY: exc.message},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return 204 No Content (no response body)
        return Response(status=status.HTTP_204_NO_CONTENT)
