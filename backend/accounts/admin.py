from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RoleActivationCode, User


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


@admin.register(RoleActivationCode)
class RoleActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'role', 'is_used', 'created_by', 'used_by', 'created_at', 'used_at')
    list_filter = ('role', 'is_used', 'created_at')
    search_fields = ('code', 'created_by__username', 'used_by__username')
    readonly_fields = ('created_at', 'used_at')
