from rest_framework.permissions import BasePermission

from accounts.utils.permissions import is_platform_admin
from teams.models import TeamMember


class IsPlatformAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return is_platform_admin(request.user)


class IsTeamMemberPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and TeamMember.objects.filter(user=user).exists())
