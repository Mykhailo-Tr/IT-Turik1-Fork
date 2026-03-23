from django.contrib import admin

from .models import Team, TeamInvitation, TeamJoinRequest, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'captain',
        'is_public',
        'organization',
        'contact_telegram',
        'contact_discord',
        'get_members_count',
    )
    search_fields = (
        'name',
        'email',
        'organization',
        'contact_telegram',
        'contact_discord',
        'captain__username',
    )

    def get_members_count(self, obj):
        return obj.members.count()

    get_members_count.short_description = 'Members count'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'user')
    search_fields = ('team__name', 'user__username', 'user__email')


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'status', 'invited_by', 'created_at', 'responded_at')
    search_fields = ('team__name', 'user__username', 'user__email', 'invited_by__username')
    list_filter = ('status', 'created_at')


@admin.register(TeamJoinRequest)
class TeamJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'status', 'reviewed_by', 'created_at', 'reviewed_at')
    search_fields = ('team__name', 'user__username', 'user__email', 'reviewed_by__username')
    list_filter = ('status', 'created_at')
