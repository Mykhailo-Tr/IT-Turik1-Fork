from django.urls import path

from .views import (
    TournamentDetailView,
    TournamentListCreateView,
    TournamentRegistrationView,
    TournamentStatusTransitionView,
)

urlpatterns = [
    path('', TournamentListCreateView.as_view(), name='tournament_list_create'),
    path('<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/register/', TournamentRegistrationView.as_view(), name='tournament_register'),
    path('<int:pk>/status/', TournamentStatusTransitionView.as_view(), name='tournament_status'),
]
