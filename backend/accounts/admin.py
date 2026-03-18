from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'needs_onboarding')
    search_fields = ('username', 'email', 'full_name')

    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional info',
            {
                'fields': ('role', 'needs_onboarding', 'full_name', 'phone', 'city'),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Additional info',
            {
                'fields': ('email', 'role', 'needs_onboarding', 'full_name', 'phone', 'city'),
            },
        ),
    )
