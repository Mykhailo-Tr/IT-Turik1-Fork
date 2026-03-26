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


class RoleActivationCode(models.Model):
    code = models.CharField(max_length=24, unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    is_used = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_role_activation_codes',
    )
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='used_role_activation_codes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['role', 'is_used'], name='role_code_role_used_idx'),
        ]

    def __str__(self):
        return f'{self.role}:{self.code}:{self.is_used}'
