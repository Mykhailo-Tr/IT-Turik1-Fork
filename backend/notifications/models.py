from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Stores a system (in-site) notification for a user.

    Each row represents one notification delivered via the 'system' channel.
    Email notifications are sent inline and do NOT create a row here.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    event_type = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read'], name='notif_recipient_read_idx'),
            models.Index(fields=['recipient', 'created_at'], name='notif_recipient_date_idx'),
        ]

    def __str__(self):
        return f'{self.event_type} → {self.recipient_id} (read={self.is_read})'
