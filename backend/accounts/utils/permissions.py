from enum import Enum


class Permission(Enum):
    CREATE_TOURNAMENT = 'create_tournament'
    EDIT_TOURNAMENT = 'edit_tournament'
    DELETE_TOURNAMENT = 'delete_tournament'
    VIEW_TOURNAMENT = 'view_tournament'
    MANAGE_PARTICIPANTS = 'manage_participants'
    SET_RESULTS = 'set_results'


TOURNAMENT_MANAGEMENT_PERMISSIONS = {
    Permission.CREATE_TOURNAMENT,
    Permission.EDIT_TOURNAMENT,
    Permission.DELETE_TOURNAMENT,
    Permission.MANAGE_PARTICIPANTS,
}

TOURNAMENT_VIEW_PERMISSIONS = {
    Permission.VIEW_TOURNAMENT,
}

JURY_TOURNAMENT_PERMISSIONS = {
    Permission.VIEW_TOURNAMENT,
    Permission.SET_RESULTS,
}

TOURNAMENT_PERMISSIONS = (
    TOURNAMENT_MANAGEMENT_PERMISSIONS
    | TOURNAMENT_VIEW_PERMISSIONS
    | {Permission.SET_RESULTS}
)

ROLE_PERMISSIONS = {
    'admin': (
        TOURNAMENT_MANAGEMENT_PERMISSIONS
        | TOURNAMENT_VIEW_PERMISSIONS
        | {Permission.SET_RESULTS}
    ),
    'organizer': (
        TOURNAMENT_MANAGEMENT_PERMISSIONS
        | TOURNAMENT_VIEW_PERMISSIONS
        | {Permission.SET_RESULTS}
    ),
    'jury': JURY_TOURNAMENT_PERMISSIONS,
}


def is_platform_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))


def user_has_permission(user, permission):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return permission in ROLE_PERMISSIONS.get(user.role, set())
