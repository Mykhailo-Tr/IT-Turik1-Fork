from django.contrib import admin

from .models import Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'captain',
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
