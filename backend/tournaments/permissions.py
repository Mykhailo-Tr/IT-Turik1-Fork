from rest_framework.permissions import BasePermission

from accounts.utils.permissions import is_platform_admin
from teams.models import TeamMember


class IsPlatformAdminPermission(BasePermission):
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return is_platform_admin(request.user)


class IsTeamMemberPermission(BasePermission):
    message = 'Team membership is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and TeamMember.objects.filter(user=user).exists())


class IsPlatformAdminOrTeamMemberPermission(BasePermission):
    message = 'Admin or team membership is required.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_platform_admin(user):
            return True
        return TeamMember.objects.filter(user=user).exists()


class IsJuryPermission(BasePermission):
    message = 'Jury access required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == 'jury')
