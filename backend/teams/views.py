from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember
from .serializers import (
    clear_invitation_states_for_member,
    clear_join_request_states_for_member,
    TeamInvitationInboxSerializer,
    TeamMemberSerializer,
    TeamSerializer,
    invite_user_to_team,
)


def get_team_queryset():
    return (
        Team.objects.select_related('captain')
        .prefetch_related(
            'members',
            Prefetch(
                'invitations',
                queryset=TeamInvitation.objects.select_related('user', 'invited_by').order_by('-created_at'),
            ),
            Prefetch(
                'join_requests',
                queryset=TeamJoinRequest.objects.select_related('user', 'reviewed_by').order_by('-created_at'),
            ),
        )
        .order_by('id')
    )


def is_team_member(team, user):
    if team.captain_id == user.id:
        return True
    return any(member.id == user.id for member in team.members.all())


class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return (
            get_team_queryset()
            .filter(
                Q(is_public=True)
                | Q(captain_id=user_id)
                | Q(team_members__user_id=user_id)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(captain=self.request.user)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return get_team_queryset()

    def get_object(self):
        team = super().get_object()
        if team.is_public or is_team_member(team, self.request.user):
            return team
        raise PermissionDenied('You do not have access to this private team.')

    def _assert_captain(self, team):
        if team.captain_id != self.request.user.id:
            return Response({'detail': 'Only captain can modify this team.'}, status=status.HTTP_403_FORBIDDEN)
        return None

    def update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)


class TeamMemberManageView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        if user.id == team.captain_id:
            return Response({'detail': 'Captain is already on the team.'}, status=status.HTTP_400_BAD_REQUEST)

        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response({'detail': 'User is already a team member.'}, status=status.HTTP_400_BAD_REQUEST)

        invitation, created = invite_user_to_team(team=team, user=user, invited_by=request.user)
        if not invitation:
            return Response({'detail': 'Unable to invite this user.'}, status=status.HTTP_400_BAD_REQUEST)

        team.refresh_from_db()
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk, user_id):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        if team.captain_id == user_id:
            return Response({'detail': 'Captain cannot be removed from team.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
        if deleted_count == 0:
            return Response({'detail': 'User is not a team member.'}, status=status.HTTP_404_NOT_FOUND)

        clear_invitation_states_for_member(team=team, user_id=user_id)
        clear_join_request_states_for_member(team=team, user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)

        if team.captain_id == request.user.id:
            return Response(
                {'detail': 'Captain cannot leave the team. Transfer captain role or delete the team.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = TeamMember.objects.filter(team=team, user=request.user).delete()
        if deleted_count == 0:
            return Response({'detail': 'You are not a team member of this team.'}, status=status.HTTP_400_BAD_REQUEST)

        clear_invitation_states_for_member(team=team, user=request.user)
        clear_join_request_states_for_member(team=team, user=request.user)
        return Response({'detail': 'You left the team.'}, status=status.HTTP_200_OK)


class TeamInvitationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamInvitationInboxSerializer

    def get_queryset(self):
        return (
            TeamInvitation.objects.select_related('team', 'invited_by')
            .filter(user=self.request.user)
            .exclude(team__team_members__user=self.request.user)
            .order_by('-created_at')
        )


class TeamInvitationRespondView(APIView):
    permission_classes = [IsAuthenticated]
    new_status = None

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            TeamInvitation.objects.select_related('team'),
            id=invitation_id,
            user=request.user,
        )

        if invitation.status != TeamInvitation.STATUS_INVITED:
            return Response(
                {'detail': 'This invitation is already processed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        if self.new_status == TeamInvitation.STATUS_ACCEPTED:
            TeamMember.objects.get_or_create(team=invitation.team, user=request.user)
            TeamJoinRequest.objects.filter(
                team=invitation.team,
                user=request.user,
                status=TeamJoinRequest.STATUS_PENDING,
            ).update(
                status=TeamJoinRequest.STATUS_DECLINED,
                reviewed_by=invitation.team.captain,
                reviewed_at=now,
            )
            clear_invitation_states_for_member(team=invitation.team, user=request.user)
        else:
            invitation.status = self.new_status
            invitation.responded_at = now
            invitation.save(update_fields=['status', 'responded_at', 'updated_at'])

        team = get_object_or_404(get_team_queryset(), pk=invitation.team_id)
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInvitationAcceptView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_ACCEPTED


class TeamInvitationDeclineView(TeamInvitationRespondView):
    new_status = TeamInvitation.STATUS_DECLINED


class TeamJoinRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        if not team.is_public:
            return Response({'detail': 'Join requests are available only for public teams.'}, status=status.HTTP_400_BAD_REQUEST)

        if is_team_member(team, request.user):
            return Response({'detail': 'You are already in this team.'}, status=status.HTTP_400_BAD_REQUEST)

        if TeamInvitation.objects.filter(
            team=team,
            user=request.user,
            status=TeamInvitation.STATUS_INVITED,
        ).exists():
            return Response({'detail': 'You already have an invitation to this team.'}, status=status.HTTP_400_BAD_REQUEST)

        join_request, created = TeamJoinRequest.objects.get_or_create(
            team=team,
            user=request.user,
            defaults={'status': TeamJoinRequest.STATUS_PENDING},
        )

        if not created:
            if join_request.status == TeamJoinRequest.STATUS_PENDING:
                return Response({'detail': 'Join request already sent.'}, status=status.HTTP_200_OK)
            join_request.status = TeamJoinRequest.STATUS_PENDING
            join_request.reviewed_by = None
            join_request.reviewed_at = None
            join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        return Response({'detail': 'Join request sent.'}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class TeamJoinRequestReviewView(APIView):
    permission_classes = [IsAuthenticated]
    new_status = None

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(get_team_queryset(), pk=pk)

    def post(self, request, pk, request_id):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can review join requests.'}, status=status.HTTP_403_FORBIDDEN)

        join_request = get_object_or_404(TeamJoinRequest, id=request_id, team=team)
        if join_request.status != TeamJoinRequest.STATUS_PENDING:
            return Response({'detail': 'This join request is already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        join_request.status = self.new_status
        join_request.reviewed_by = request.user
        join_request.reviewed_at = now
        join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

        if self.new_status == TeamJoinRequest.STATUS_ACCEPTED:
            TeamMember.objects.get_or_create(team=team, user=join_request.user)
            clear_invitation_states_for_member(team=team, user=join_request.user)

        team.refresh_from_db()
        serializer = TeamSerializer(team, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamJoinRequestAcceptView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_ACCEPTED


class TeamJoinRequestDeclineView(TeamJoinRequestReviewView):
    new_status = TeamJoinRequest.STATUS_DECLINED


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(full_name__icontains=search)
            )
        return queryset
