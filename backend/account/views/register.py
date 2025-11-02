"""API views for account endpoints."""
from __future__ import annotations

from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers import RegisterUserSerializer
from account.exceptions import RegistrationConflictError, RegistrationValidationError
from account.services import RegistrationService


class RegisterUserView(APIView):
    """Handle user registration via POST /api/v1/auth/register."""

    authentication_classes = []
    permission_classes = [AllowAny]
    service_class = RegistrationService

    def post(self, request: Request) -> Response:
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        command = serializer.to_command()

        service = self.service_class()
        try:
            user_profile = service.execute(command)
        except RegistrationValidationError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        except RegistrationConflictError as exc:
            return Response({
                "detail": exc.message, "field": exc.field
            }, status=status.HTTP_409_CONFLICT)

        # Dataclasses convert cleanly to JSON-ready primitives for Response.
        payload = asdict(user_profile)
        return Response(payload, status=status.HTTP_201_CREATED)
