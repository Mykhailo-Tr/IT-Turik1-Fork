from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Tournament(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_REGISTRATION = 'registration'
    STATUS_RUNNING = 'running'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_REGISTRATION, 'Registration'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_FINISHED, 'Finished'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    registration_start = models.DateTimeField(blank=True, null=True)
    registration_end = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    max_teams = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_tournaments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    teams = models.ManyToManyField('teams.Team', through='TournamentTeam', related_name='tournaments')

    class Meta:
        db_table = 'tournaments'
        indexes = [
            models.Index(fields=['status'], name='tourn_status_idx'),
            models.Index(fields=['registration_start', 'registration_end'], name='tourn_reg_window_idx'),
            models.Index(fields=['start_date', 'end_date'], name='tourn_run_window_idx'),
            models.Index(fields=['created_by'], name='tourn_creator_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(max_teams__isnull=True) | Q(max_teams__gt=0),
                name='tourn_max_teams_pos_or_null',
            ),
        ]

    def clean(self):
        errors = {}

        if self.max_teams is not None and self.max_teams <= 0:
            errors['max_teams'] = 'Max teams must be greater than zero.'

        if self.registration_start and self.registration_end and self.registration_start > self.registration_end:
            errors['registration_end'] = 'Registration end must be greater than or equal to registration start.'

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = 'Tournament end must be greater than or equal to tournament start.'

        if self.registration_end and self.end_date and self.registration_end > self.end_date:
            errors['registration_end'] = 'Registration end cannot be after tournament end.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.title


class TournamentTeam(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name='tournament_teams')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team_tournaments')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tournament_teams'
        unique_together = (('tournament', 'team'),)
        indexes = [
            models.Index(fields=['tournament', 'team'], name='tourn_teams_idx_0'),
            models.Index(fields=['team', 'tournament'], name='tourn_teams_idx_1'),
        ]

    def __str__(self):
        return f'{self.tournament_id}:{self.team_id}'
