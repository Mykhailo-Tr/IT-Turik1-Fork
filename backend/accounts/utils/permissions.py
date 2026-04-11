def is_platform_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))
