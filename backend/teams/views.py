from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import Team, TeamMember
from .serializers import TeamMemberSerializer, TeamSerializer


class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.select_related('captain').prefetch_related('members').all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(captain=self.request.user)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.select_related('captain').prefetch_related('members').all()

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
        return get_object_or_404(Team.objects.select_related('captain').prefetch_related('members'), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        TeamMember.objects.get_or_create(team=team, user=user)

        team.refresh_from_db()
        return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)

    def delete(self, request, pk, user_id):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        if team.captain_id == user_id:
            return Response({'detail': 'Captain cannot be removed from team.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
        if deleted_count == 0:
            return Response({'detail': 'User is not a team member.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


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
