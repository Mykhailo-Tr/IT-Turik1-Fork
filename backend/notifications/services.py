import logging

from .channels import CHANNEL_REGISTRY
from .config import EVENTS

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Central entry-point for sending notifications.

    Usage::

        from notifications.services import NotificationService

        NotificationService.notify(
            recipients=[user],
            event_type='team_invitation_received',
            context={'team_name': team.name, 'invited_by': captain.username},
        )
    """

    @classmethod
    def notify(cls, *, recipients, event_type, context=None):
        """
        Dispatch a notification to *recipients* for the given *event_type*.
        """
        event = EVENTS.get(event_type)
        if not event:
            logger.warning('NotificationService: unknown event_type=%s', event_type)
            return

        # Use the event object's OOP logic to format content
        title, message, email_subject = event.format(context)
        channel_names = event.channels

        for channel_name in channel_names:
            channel_cls = CHANNEL_REGISTRY.get(channel_name)
            if not channel_cls:
                logger.warning(
                    'NotificationService: unknown channel=%s for event=%s',
                    channel_name,
                    event_type,
                )
                continue

            channel = channel_cls()
            for recipient in recipients:
                channel.send(
                    recipient=recipient,
                    title=title,
                    message=message,
                    event_type=event_type,
                    email_subject=email_subject,
                )
