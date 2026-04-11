from django.urls import path

from ..views import (
    TeamInvitationAcceptView,
    TeamInvitationDeclineView,
    TeamInvitationListView,
)

urlpatterns = [
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