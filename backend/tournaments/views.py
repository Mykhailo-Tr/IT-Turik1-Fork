from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.utils.permissions import is_platform_admin
from teams.models import TeamMember

from .models import Round, Submission, Tournament
from .permissions import IsPlatformAdminPermission
from .serializers import (
    CurrentTaskSerializer,
    OwnSubmissionSerializer,
    RoundSerializer,
    SubmissionSerializer,
    TournamentAdminSerializer,
    TournamentPublicSerializer,
)
from .services import mark_round_evaluated, start_round, sync_time_based_statuses


def get_tournament_queryset():
    return Tournament.objects.prefetch_related(
        Prefetch('rounds', queryset=Round.objects.order_by('position'))
    ).order_by('-created_at')


def get_round_queryset():
    return Round.objects.select_related('tournament').order_by('tournament_id', 'position')


def get_own_submissions_queryset(user):
    return (
        Submission.objects.select_related('team', 'round', 'round__tournament')
        .filter(Q(team__captain_id=user.id) | Q(team__team_members__user_id=user.id))
        .distinct()
        .order_by('-updated_at')
    )


class TournamentListView(generics.ListAPIView):
    queryset = get_tournament_queryset()
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer

    def list(self, request, *args, **kwargs):
        sync_time_based_statuses()
        return super().list(request, *args, **kwargs)


class TournamentDetailView(generics.RetrieveAPIView):
    queryset = get_tournament_queryset()
    permission_classes = [AllowAny]
    serializer_class = TournamentPublicSerializer

    def retrieve(self, request, *args, **kwargs):
        sync_time_based_statuses()
        return super().retrieve(request, *args, **kwargs)


class TournamentCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request):
        serializer = TournamentAdminSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = TournamentAdminSerializer(tournament, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        serializer = TournamentAdminSerializer(
            tournament,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save()
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)


class TournamentStartRegistrationView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        if tournament.status != Tournament.STATUS_DRAFT:
            raise ValidationError({'status': ['Only draft tournaments can be moved to registration.']})

        tournament.status = Tournament.STATUS_REGISTRATION
        tournament.save(update_fields=['status', 'updated_at'])
        return Response(TournamentPublicSerializer(tournament).data, status=status.HTTP_200_OK)


class RoundListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]
    serializer_class = RoundSerializer

    def get_queryset(self):
        queryset = get_round_queryset()
        tournament_id = self.request.query_params.get('tournament_id')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset


class RoundDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]
    serializer_class = RoundSerializer

    def get_queryset(self):
        return get_round_queryset()


class RoundStartView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        sync_time_based_statuses()
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        start_round(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class RoundMarkEvaluatedView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        sync_time_based_statuses()
        round_obj = get_object_or_404(get_round_queryset(), pk=pk)
        mark_round_evaluated(round_obj)
        round_obj.refresh_from_db()
        return Response(RoundSerializer(round_obj).data, status=status.HTTP_200_OK)


class SubmissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        sync_time_based_statuses()
        return get_own_submissions_queryset(self.request.user)


class SubmissionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OwnSubmissionSerializer
        return SubmissionSerializer

    def get_queryset(self):
        sync_time_based_statuses()
        return get_own_submissions_queryset(self.request.user)


class CurrentTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sync_time_based_statuses()

        if not is_platform_admin(request.user) and not TeamMember.objects.filter(user=request.user).exists():
            raise PermissionDenied('Team membership is required to view current task.')

        queryset = (
            Round.objects.select_related('tournament')
            .filter(
                status=Round.STATUS_ACTIVE,
                tournament__status=Tournament.STATUS_RUNNING,
            )
            .order_by('end_date', 'id')
        )

        tournament_id = request.query_params.get('tournament_id')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        active_round = queryset.first()
        if not active_round:
            raise NotFound('No active round is available right now.')

        return Response(CurrentTaskSerializer(active_round).data, status=status.HTTP_200_OK)
