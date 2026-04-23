from django.urls import path

from .views import (
    CurrentTaskView,
    RoundCloseSubmissionsView,
    RoundDetailView,
    RoundListCreateView,
    RoundMarkEvaluatedView,
    RoundStartView,
    SubmissionDetailView,
    SubmissionListCreateView,
    TournamentCreateView,
    TournamentDetailView,
    TournamentListView,
    TournamentStartRegistrationView,
    TournamentTeamRegistrationCreateView,
    TournamentUpdateView,
)

urlpatterns = [
    path('', TournamentListView.as_view(), name='tournaments'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('manage/', TournamentCreateView.as_view(), name='tournament_manage_create'),
    path('manage/<int:pk>/', TournamentUpdateView.as_view(), name='tournament_manage_update'),
    path(
        '<int:pk>/start-registration/',
        TournamentStartRegistrationView.as_view(),
        name='tournament_start_registration',
    ),
    path('<int:pk>/register-team/', TournamentTeamRegistrationCreateView.as_view(), name='tournament_register_team'),
    path('rounds/', RoundListCreateView.as_view(), name='rounds'),
    path('rounds/<int:pk>/', RoundDetailView.as_view(), name='round_detail'),
    path('rounds/<int:pk>/start/', RoundStartView.as_view(), name='round_start'),
    path('rounds/<int:pk>/close-submissions/', RoundCloseSubmissionsView.as_view(), name='round_close_submissions'),
    path('rounds/<int:pk>/mark-evaluated/', RoundMarkEvaluatedView.as_view(), name='round_mark_evaluated'),
    path('submissions/', SubmissionListCreateView.as_view(), name='submissions'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('current-task/', CurrentTaskView.as_view(), name='current_task'),
]
