from django.urls import path

from .views import TournamentRegistrationView, TournamentStatusTransitionView

urlpatterns = [
    path('<int:pk>/register/', TournamentRegistrationView.as_view(), name='tournament_register'),
    path('<int:pk>/status/', TournamentStatusTransitionView.as_view(), name='tournament_status'),
]
