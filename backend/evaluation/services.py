import random
from django.db import transaction
from rest_framework.exceptions import ValidationError
from accounts.models import User
from tournaments.models import Round
from .models import JuryAssignment


@transaction.atomic
def assign_submissions_to_jury(round_obj, k=2):
    if round_obj.status != Round.STATUS_SUBMISSION_CLOSED:
        raise ValidationError({'status': 'Round must be submission_closed before assignment.'})

    submissions = list(round_obj.submissions.all())
    juries = list(User.objects.filter(role='jury'))

    if not juries:
        raise ValidationError({'jury': 'No jury members found to assign submissions.'})

    # Adjust k if there are not enough jurors
    actual_k = min(k, len(juries))

    for submission in submissions:
        # Get random sample of juries
        assigned_juries = random.sample(juries, actual_k)
        for jury in assigned_juries:
            JuryAssignment.objects.get_or_create(
                submission=submission,
                jury=jury,
            )

    return round_obj
