from django.urls import path

from .views import (
    TeamDetailView,
    TeamLeaveView,
    TeamListCreateView,
)

from .urls.members import urlpatterns as member_urls
from .urls.invitations import urlpatterns as invitation_urls
from .urls.join_requests import urlpatterns as join_request_urls

urlpatterns = [
    path('', TeamListCreateView.as_view(), name='teams'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/leave/', TeamLeaveView.as_view(), name='team_leave'),

    *member_urls,
    *invitation_urls,
    *join_request_urls,
]
