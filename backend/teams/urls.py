from django.urls import path

from .views import (
    TeamDetailView,
    TeamInfoMembersView,
    TeamInfoView,
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
    path('', TeamListCreateView.as_view(), name='teams'),
    path('<int:pk>/info/', TeamInfoView.as_view(), name='team_info'),
    path('<int:pk>/info-members/', TeamInfoMembersView.as_view(), name='team_info_members'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),
    path('<int:pk>/members/', TeamMemberManageView.as_view(), name='team_members'),
    path('<int:pk>/members/<int:user_id>/', TeamMemberManageView.as_view(), name='team_member_detail'),
    path('<int:pk>/join-requests/', TeamJoinRequestCreateView.as_view(), name='team_join_request_create'),
    path(
        '<int:pk>/join-requests/<int:request_id>/accept/',
        TeamJoinRequestAcceptView.as_view(),
        name='team_join_request_accept',
    ),
    path(
        '<int:pk>/join-requests/<int:request_id>/decline/',
        TeamJoinRequestDeclineView.as_view(),
        name='team_join_request_decline',
    ),
    path('invitations/', TeamInvitationListView.as_view(), name='team_invitations'),
    path(
        'invitations/<int:invitation_id>/accept/',
        TeamInvitationAcceptView.as_view(),
        name='team_invitation_accept',
    ),
    path(
        'invitations/<int:invitation_id>/decline/',
        TeamInvitationDeclineView.as_view(),
        name='team_invitation_decline',
    ),
]
