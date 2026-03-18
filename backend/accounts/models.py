from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('team', 'Team Member'),
        ('jury', 'Jury'),
        ('organizer', 'Organizer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team')
    needs_onboarding = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Team(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    captain = models.ForeignKey('User', on_delete=models.PROTECT, related_name='captained_teams')
    organization = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    members = models.ManyToManyField('User', through='TeamMember', related_name='teams')

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_members')

    class Meta:
        unique_together = (('user', 'team'),)
        indexes = [
            models.Index(fields=['user', 'team'], name='team_members_index_0'),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.team_id}'
