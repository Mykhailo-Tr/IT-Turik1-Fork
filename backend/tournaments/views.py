from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tournament
from .serializers import (
    StatusTransitionSerializer,
    TournamentReadSerializer,
    TournamentTeamRegistrationSerializer,
)


def is_platform_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))


class TournamentRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament.objects.select_related('created_by'), pk=pk)

        serializer = TournamentTeamRegistrationSerializer(
            data=request.data,
            tournament=tournament,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        tournament.refresh_from_db()
        return Response(
            TournamentReadSerializer(tournament).data,
            status=status.HTTP_201_CREATED,
        )


class TournamentStatusTransitionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament.objects.select_related('created_by'), pk=pk)

        if not is_platform_admin(request.user) and tournament.created_by_id != request.user.id:
            raise PermissionDenied('Only the tournament creator or a platform admin can change status.')

        serializer = StatusTransitionSerializer(
            data=request.data,
            tournament=tournament,
        )
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()

        return Response(
            TournamentReadSerializer(tournament).data,
            status=status.HTTP_200_OK,
        )
