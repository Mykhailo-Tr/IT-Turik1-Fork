from django.contrib import admin

from .models import Tournament, TournamentTeam


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'start_date', 'end_date', 'max_teams', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title',)
    autocomplete_fields = ('created_by', 'teams')


@admin.register(TournamentTeam)
class TournamentTeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'team', 'joined_at')
    list_filter = ('joined_at',)
    autocomplete_fields = ('tournament', 'team')
