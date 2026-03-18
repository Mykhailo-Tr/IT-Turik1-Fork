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
