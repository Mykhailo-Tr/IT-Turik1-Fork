from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Tournament
from .serializers import (
    StatusTransitionSerializer,
    TournamentReadSerializer,
    TournamentTeamRegistrationSerializer,
    TournamentWriteSerializer,
)


def is_platform_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))


ALLOWED_ORDERINGS = {'start_date', '-start_date', 'created_at', '-created_at', 'title', '-title'}


class TournamentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TournamentWriteSerializer
        return TournamentReadSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Tournament.objects.select_related('created_by').order_by('-created_at')

        if is_platform_admin(user):
            pass
        else:
            qs = qs.filter(Q(created_by=user) | ~Q(status=Tournament.STATUS_DRAFT))

        params = self.request.query_params

        status_filter = params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = params.get('search')
        if search:
            qs = qs.filter(title__icontains=search)

        created_by = params.get('created_by')
        if created_by:
            qs = qs.filter(created_by_id=created_by)

        if params.get('registration_open') == 'true':
            now = timezone.now()
            qs = qs.filter(
                status=Tournament.STATUS_REGISTRATION,
                registration_start__lte=now,
                registration_end__gte=now,
            )

        start_date_from = params.get('start_date_from')
        if start_date_from:
            qs = qs.filter(start_date__gte=start_date_from)

        start_date_to = params.get('start_date_to')
        if start_date_to:
            qs = qs.filter(start_date__lte=start_date_to)

        ordering = params.get('ordering')
        if ordering and ordering in ALLOWED_ORDERINGS:
            qs = qs.order_by(ordering)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ('admin', 'organizer') and not user.is_superuser:
            raise PermissionDenied('Only admins and organizers can create tournaments.')
        serializer.save(created_by=user)


class TournamentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TournamentWriteSerializer
        return TournamentReadSerializer

    def get_queryset(self):
        return Tournament.objects.select_related('created_by')

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if obj.status == Tournament.STATUS_DRAFT and obj.created_by_id != user.id and not is_platform_admin(user):
            raise Http404
        return obj

    def _assert_owner_or_admin(self, obj):
        user = self.request.user
        if obj.created_by_id != user.id and not is_platform_admin(user):
            raise PermissionDenied('Only the tournament creator or a platform admin can modify this tournament.')

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        self._assert_owner_or_admin(obj)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self._assert_owner_or_admin(obj)
        return super().destroy(request, *args, **kwargs)


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
