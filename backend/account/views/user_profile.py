"""API views for user profile endpoint."""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers.user_profile import UserProfileSerializer
from account.services.user_profile_service import UserProfileService


class UserProfileView(APIView):
    """Handle retrieval of authenticated user's profile via GET /api/v1/auth/me.

    Returns the authenticated user's full profile (id, username, email, created_at).
    Requires authentication via JWT cookie.
    User can only access their own profile - automatic isolation via request.user.
    """

    permission_classes = [IsAuthenticated]
    service_class = UserProfileService
    serializer_class = UserProfileSerializer

    def get(self, request: Request) -> Response:
        """Handle GET /api/v1/auth/me.

        Retrieves the authenticated user's profile data.

        Args:
            request: Authenticated HTTP request with user set by JWT authentication.

        Returns:
            Response with 200 OK status and user profile data:
            {
                "id": 123,
                "username": "user123",
                "email": "user@example.com",
                "created_at": "2025-10-24T12:34:56Z"
            }

        Raises:
            404 Not Found: If user from JWT token no longer exists in database
                (very rare edge case).
            401 Unauthorized: If user is not authenticated (handled by
                IsAuthenticated permission class automatically).

        Notes:
            - User can only access their own profile (request.user.id)
            - Sensitive fields (password, is_staff, etc.) are excluded
            - created_at timestamp is in ISO 8601 format
        """
        service = self.service_class()

        try:
            profile_dto = service.execute(user_id=request.user.id)
        except request.user.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class()
        serialized_data = serializer.to_representation(profile_dto)

        return Response(serialized_data, status=status.HTTP_200_OK)
