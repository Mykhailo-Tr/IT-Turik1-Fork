from django.urls import path

from .views import TeamDetailView, TeamListCreateView, TeamMemberManageView, UserListView

urlpatterns = [
    path('teams/', TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/members/', TeamMemberManageView.as_view(), name='team_members'),
    path('teams/<int:pk>/members/<int:user_id>/', TeamMemberManageView.as_view(), name='team_member_detail'),
    path('users/', UserListView.as_view(), name='users'),
]
