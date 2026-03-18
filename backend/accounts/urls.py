from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ActivationView,
    GoogleAuthView,
    RegisterView,
    TeamDetailView,
    TeamListCreateView,
    TeamMemberManageView,
    UserListView,
    UserProfileView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('google-login/', GoogleAuthView.as_view(), name='google_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('teams/', TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/members/', TeamMemberManageView.as_view(), name='team_members'),
    path('teams/<int:pk>/members/<int:user_id>/', TeamMemberManageView.as_view(), name='team_member_detail'),
    path('users/', UserListView.as_view(), name='users'),
]
