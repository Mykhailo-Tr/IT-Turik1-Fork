from django.urls import path

from .views import (
    CurrentTaskView,
    RoundDetailView,
    RoundListCreateView,
    RoundMarkEvaluatedView,
    RoundStartView,
    SubmissionDetailView,
    SubmissionListCreateView,
    TournamentDetailView,
    TournamentListCreateView,
    TournamentStartRegistrationView,
)

urlpatterns = [
    path('', TournamentListCreateView.as_view(), name='tournaments'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/start-registration/', TournamentStartRegistrationView.as_view(), name='tournament_start_registration'),
    path('rounds/', RoundListCreateView.as_view(), name='rounds'),
    path('rounds/<int:pk>/', RoundDetailView.as_view(), name='round_detail'),
    path('rounds/<int:pk>/start/', RoundStartView.as_view(), name='round_start'),
    path('rounds/<int:pk>/mark-evaluated/', RoundMarkEvaluatedView.as_view(), name='round_mark_evaluated'),
    path('submissions/', SubmissionListCreateView.as_view(), name='submissions'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('current-task/', CurrentTaskView.as_view(), name='current_task'),
]
