from django.contrib import admin

from .models import Round, Submission, Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'start_date', 'end_date', 'rounds_count')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'position', 'name', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'evaluation_criteria')
    search_fields = ('name', 'tournament__name')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'round', 'github_url', 'updated_at')
    search_fields = ('team__name', 'round__name', 'github_url')
