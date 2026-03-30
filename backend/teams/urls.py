from django.urls import path

from .views import (
    TeamDetailView,
    TeamInvitationAcceptView,
    TeamInvitationDeclineView,
    TeamInvitationListView,
    TeamJoinRequestAcceptView,
    TeamJoinRequestCreateView,
    TeamJoinRequestDeclineView,
    TeamLeaveView,
    TeamListCreateView,
    TeamMemberManageView,
)

urlpatterns = [
    path('teams/', TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),
    path('teams/<int:pk>/members/', TeamMemberManageView.as_view(), name='team_members'),
    path('teams/<int:pk>/members/<int:user_id>/', TeamMemberManageView.as_view(), name='team_member_detail'),
    path('teams/<int:pk>/join-requests/', TeamJoinRequestCreateView.as_view(), name='team_join_request_create'),
    path(
        'teams/<int:pk>/join-requests/<int:request_id>/accept/',
        TeamJoinRequestAcceptView.as_view(),
        name='team_join_request_accept',
    ),
    path(
        'teams/<int:pk>/join-requests/<int:request_id>/decline/',
        TeamJoinRequestDeclineView.as_view(),
        name='team_join_request_decline',
    ),
    path('teams/invitations/', TeamInvitationListView.as_view(), name='team_invitations'),
    path(
        'teams/invitations/<int:invitation_id>/accept/',
        TeamInvitationAcceptView.as_view(),
        name='team_invitation_accept',
    ),
    path(
        'teams/invitations/<int:invitation_id>/decline/',
        TeamInvitationDeclineView.as_view(),
        name='team_invitation_decline',
    ),
]
