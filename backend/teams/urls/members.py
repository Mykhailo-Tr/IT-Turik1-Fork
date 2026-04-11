from django.urls import path
from ..views import TeamMemberManageView


urlpatterns = [
    path('<int:pk>/members/', TeamMemberManageView.as_view(), name='team_members'),
    path('<int:pk>/members/<int:user_id>/', TeamMemberManageView.as_view(), name='team_member_detail'),
]
