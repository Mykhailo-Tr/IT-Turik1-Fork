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

    submissions = list(round_obj.submissions.select_for_update())
    jury_ids = list(User.objects.filter(role='jury').values_list('id', flat=True))

    if not jury_ids:
        raise ValidationError({'jury': 'No jury members found to assign submissions.'})

    actual_k = min(k, len(jury_ids))
    if actual_k <= 0 or not submissions:
        return round_obj

    submission_ids = [submission.id for submission in submissions]
    existing_pairs = JuryAssignment.objects.filter(
        submission_id__in=submission_ids,
    ).values_list('submission_id', 'jury_id')

    existing_by_submission = {submission_id: set() for submission_id in submission_ids}
    for submission_id, jury_id in existing_pairs:
        existing_by_submission.setdefault(submission_id, set()).add(jury_id)

    new_assignments = []
    for submission in submissions:
        existing_jurors = existing_by_submission.get(submission.id, set())
        needed = actual_k - len(existing_jurors)
        if needed <= 0:
            continue

        available_juror_ids = [jury_id for jury_id in jury_ids if jury_id not in existing_jurors]
        if not available_juror_ids:
            continue

        sample_size = min(needed, len(available_juror_ids))
        selected_juror_ids = random.sample(available_juror_ids, sample_size)
        for jury_id in selected_juror_ids:
            new_assignments.append(
                JuryAssignment(
                    submission_id=submission.id,
                    jury_id=jury_id,
                )
            )

    if new_assignments:
        JuryAssignment.objects.bulk_create(new_assignments, ignore_conflicts=True)

    return round_obj
