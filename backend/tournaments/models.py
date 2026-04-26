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

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    criteria = models.JSONField(default=list, blank=True)
    max_teams = models.PositiveIntegerField(blank=True, null=True)
    min_team_members = models.PositiveIntegerField(blank=True, null=True)
    rounds_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_tournaments',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        if self.rounds_count < 1:
            errors['rounds_count'] = 'rounds_count must be at least 1.'

        if self.min_team_members is not None and self.min_team_members < 1:
            errors['min_team_members'] = 'min_team_members must be at least 1.'

        if self.max_teams is not None and self.max_teams < 1:
            errors['max_teams'] = 'max_teams must be at least 1.'

        if not isinstance(self.criteria, list):
            errors['criteria'] = 'Criteria must be a list.'
        else:
            seen_ids = set()
            for idx, c in enumerate(self.criteria):
                if not isinstance(c, dict):
                    errors['criteria'] = f'Item at index {idx} must be an object.'
                    break
                
                c_id = c.get('id')
                name = c.get('name')
                max_score = c.get('max_score')
                
                if not c_id or not isinstance(c_id, str):
                    errors['criteria'] = f'Item at index {idx} must have a valid string "id".'
                    break
                if not name or not isinstance(name, str):
                    errors['criteria'] = f'Item "{c_id}" must have a valid string "name".'
                    break
                if max_score is None or not isinstance(max_score, (int, float)) or max_score <= 0:
                    errors['criteria'] = f'Item "{c_id}" must have a positive "max_score".'
                    break
                    
                if c_id in seen_ids:
                    errors['criteria'] = f'Duplicate criteria id: "{c_id}".'
                    break
                seen_ids.add(c_id)

        if errors:
            raise ValidationError(errors)


class Round(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_SUBMISSION_CLOSED = 'submission_closed'
    STATUS_EVALUATED = 'evaluated'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUBMISSION_CLOSED, 'SubmissionClosed'),
        (STATUS_EVALUATED, 'Evaluated'),
    )

    EVALUATION_SCORE = 'score'

    EVALUATION_CRITERIA_CHOICES = (
        (EVALUATION_SCORE, 'Score'),
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    position = models.PositiveIntegerField()
    name = models.CharField(max_length=255, blank=True)
    description = models.JSONField(default=dict, blank=True)
    tech_requirements = models.JSONField(default=dict, blank=True)
    must_have_requirements = models.JSONField(default=dict, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    passing_count = models.PositiveIntegerField(blank=True, null=True)
    winners_count = models.PositiveIntegerField(blank=True, null=True)
    evaluation_criteria = models.CharField(
        max_length=32,
        choices=EVALUATION_CRITERIA_CHOICES,
        default=EVALUATION_SCORE,
    )
    materials = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('tournament_id', 'position')
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'position'],
                name='uniq_round_tournament_position',
            ),
            models.UniqueConstraint(
                fields=['tournament'],
                condition=Q(status='active'),
                name='uniq_active_round_per_tournament',
            ),
        ]

    def __str__(self):
        return f'{self.tournament_id}:{self.position}:{self.name or self.default_name}'

    @property
    def default_name(self):
        return f'Round {self.position}'

    @property
    def is_submission_open(self):
        return self.status == self.STATUS_ACTIVE

    def clean(self):
        errors = {}

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        tournament = self.tournament
        if tournament and self.start_date and self.end_date:
            if self.start_date < tournament.start_date or self.end_date > tournament.end_date:
                errors['start_date'] = 'Round dates must be within tournament dates.'

            if tournament.rounds_count == 1:
                if self.start_date != tournament.start_date or self.end_date != tournament.end_date:
                    errors['start_date'] = 'For single-round tournaments, round dates must match tournament dates.'

        if self.position < 1:
            errors['position'] = 'position must be at least 1.'
        if tournament and self.position > tournament.rounds_count:
            errors['position'] = 'position must be less than or equal to tournament rounds_count.'

        if tournament and self.winners_count is not None and self.position != tournament.rounds_count:
            errors['winners_count'] = 'winners_count is allowed only for the last round.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.default_name
        super().save(*args, **kwargs)


class Submission(models.Model):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='submissions')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='submissions')
    github_url = models.URLField()
    demo_video_url = models.URLField(blank=True)
    demo_video_file = models.FileField(upload_to='tournaments/demo_videos/', blank=True)
    live_demo_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_submissions',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(fields=['team', 'round'], name='uniq_submission_team_round'),
        ]

    def __str__(self):
        return f'{self.team_id}:{self.round_id}'

    def clean(self):
        errors = {}

        if not self.github_url:
            errors['github_url'] = 'github_url is required.'

        if not self.demo_video_url and not self.demo_video_file:
            errors['demo_video_url'] = 'Provide demo_video_url or demo_video_file.'

        if self.round and self.round.status != Round.STATUS_ACTIVE:
            errors['round'] = 'Round is closed for submissions.'

        if errors:
            raise ValidationError(errors)


class TournamentTeamRegistration(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='team_registrations',
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='tournament_registrations',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_tournament_team_registrations',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'team'],
                name='uniq_tournament_team_registration',
            ),
        ]

    def __str__(self):
        return f'{self.tournament_id}:{self.team_id}'


