from django.conf import settings
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='captained_teams')
    organization = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TeamMember', related_name='teams')

    class Meta:
        db_table = 'accounts_team'

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_members')

    class Meta:
        db_table = 'accounts_teammember'
        unique_together = (('user', 'team'),)
        indexes = [
            models.Index(fields=['user', 'team'], name='team_members_index_0'),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.team_id}'
