from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Team, TeamMember, User


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


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'captain', 'organization', 'contact', 'get_members_count')
    search_fields = ('name', 'email', 'organization', 'contact', 'captain__username')

    def get_members_count(self, obj):
        return obj.members.count()

    get_members_count.short_description = 'Members count'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'user')
    search_fields = ('team__name', 'user__username', 'user__email')
