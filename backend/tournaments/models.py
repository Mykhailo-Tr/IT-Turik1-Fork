from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


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

    VALID_STATUS_TRANSITIONS = {
        STATUS_DRAFT: {STATUS_REGISTRATION, STATUS_RUNNING},
        STATUS_REGISTRATION: {STATUS_RUNNING},
        STATUS_RUNNING: {STATUS_FINISHED},
        STATUS_FINISHED: set(),
    }

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    registration_start = models.DateTimeField(blank=True, null=True)
    registration_end = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    max_teams = models.PositiveIntegerField(blank=True, null=True)
    min_teams = models.PositiveIntegerField(default=2)
    rounds_count = models.PositiveIntegerField(default=1)
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
            models.CheckConstraint(
                condition=Q(min_teams__gte=2),
                name='tourn_min_teams_floor',
            ),
            models.CheckConstraint(
                condition=Q(rounds_count__gte=1),
                name='tourn_rounds_count_pos',
            ),
        ]

    def clean(self):
        errors = {}

        if self.max_teams is not None and self.max_teams <= 0:
            errors['max_teams'] = 'Max teams must be greater than zero.'

        if self.min_teams < 2:
            errors['min_teams'] = 'Minimum team size cannot be less than 2.'

        if self.rounds_count < 1:
            errors['rounds_count'] = 'Rounds count must be at least 1.'

        if self.registration_start and self.registration_end and self.registration_start >= self.registration_end:
            errors['registration_end'] = 'Registration end must be after registration start.'

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            errors['end_date'] = 'Tournament end must be after tournament start.'

        if self.registration_end and self.start_date and self.registration_end > self.start_date:
            errors['registration_end'] = 'Registration must close before the tournament starts.'

        if self.registration_end and self.end_date and self.registration_end > self.end_date:
            errors.setdefault('registration_end', 'Registration end cannot be after tournament end.')

        if errors:
            raise ValidationError(errors)

    def validate_status_transition(self, new_status):
        allowed = self.VALID_STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationError(
                {'status': f'Cannot transition from "{self.status}" to "{new_status}".'}
            )

    def save(self, **kwargs):
        if not kwargs.pop('skip_auto_status', False):
            self._auto_advance_status()
        super().save(**kwargs)

    def _auto_advance_status(self):
        now = timezone.now()

        if self.status == self.STATUS_DRAFT:
            if self.registration_start and now >= self.registration_start:
                self.status = self.STATUS_REGISTRATION
            elif self.start_date and now >= self.start_date:
                self.status = self.STATUS_RUNNING

        if self.status == self.STATUS_REGISTRATION:
            if self.start_date and now >= self.start_date:
                self.status = self.STATUS_RUNNING

        if self.status == self.STATUS_RUNNING:
            if self.end_date and now >= self.end_date:
                self.status = self.STATUS_FINISHED

    @property
    def registered_teams_count(self):
        return self.tournament_teams.count()

    def is_registration_open(self):
        if self.status != self.STATUS_REGISTRATION:
            return False
        now = timezone.now()
        if self.registration_start and now < self.registration_start:
            return False
        if self.registration_end and now > self.registration_end:
            return False
        return True

    def can_accept_teams(self):
        if not self.is_registration_open():
            return False
        if self.max_teams is not None and self.registered_teams_count >= self.max_teams:
            return False
        return True

    def effective_min_teams(self):
        return max(self.min_teams, 2)

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
