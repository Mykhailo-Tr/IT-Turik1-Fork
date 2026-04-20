from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Round, Tournament


def _set_tournament_finished_if_all_rounds_evaluated(*, tournament):
    if tournament.status != Tournament.STATUS_RUNNING:
        return False

    has_pending_rounds = tournament.rounds.exclude(status=Round.STATUS_EVALUATED).exists()
    if has_pending_rounds:
        return False

    tournament.status = Tournament.STATUS_FINISHED
    tournament.save(update_fields=['status', 'updated_at'])
    return True


@transaction.atomic
def ensure_round_placeholders(tournament):
    existing_count = tournament.rounds.count()
    if existing_count > tournament.rounds_count:
        raise ValidationError({'rounds_count': 'Cannot be less than existing rounds count.'})

    for position in range(existing_count + 1, tournament.rounds_count + 1):
        Round.objects.create(
            tournament=tournament,
            position=position,
            start_date=tournament.start_date,
            end_date=tournament.end_date,
            status=Round.STATUS_DRAFT,
        )


@transaction.atomic
def start_registration(tournament):
    if tournament.status != Tournament.STATUS_DRAFT:
        raise ValidationError({'status': 'Only draft tournaments can be moved to registration.'})

    tournament.status = Tournament.STATUS_REGISTRATION
    tournament.save(update_fields=['status', 'updated_at'])
    return tournament


@transaction.atomic
def start_round(round_obj):
    now = timezone.now()
    round_obj = Round.objects.select_for_update().select_related('tournament').get(id=round_obj.id)
    tournament = round_obj.tournament

    if round_obj.status != Round.STATUS_DRAFT:
        raise ValidationError({'status': 'Only draft rounds can be started.'})

    if round_obj.start_date > now:
        raise ValidationError({'start_date': 'Round start_date has not been reached yet.'})

    if round_obj.end_date <= now:
        raise ValidationError({'end_date': 'Round already passed its deadline.'})

    if tournament.status not in {Tournament.STATUS_REGISTRATION, Tournament.STATUS_RUNNING}:
        raise ValidationError({'tournament': 'Tournament must be in registration or running status.'})

    if round_obj.position == 1 and tournament.status != Tournament.STATUS_REGISTRATION:
        raise ValidationError({'tournament': 'First round can start only from registration status.'})

    if round_obj.position > 1:
        prev_round = (
            Round.objects.filter(tournament=tournament, position=round_obj.position - 1)
            .only('status')
            .first()
        )
        if prev_round is None or prev_round.status != Round.STATUS_EVALUATED:
            raise ValidationError({'status': 'Previous round must be evaluated before starting the next round.'})

    if Round.objects.filter(tournament=tournament, status=Round.STATUS_ACTIVE).exclude(id=round_obj.id).exists():
        raise ValidationError({'status': 'Another round is already active for this tournament.'})

    round_obj.status = Round.STATUS_ACTIVE
    round_obj.save(update_fields=['status', 'updated_at'])

    if tournament.status != Tournament.STATUS_RUNNING:
        tournament.status = Tournament.STATUS_RUNNING
        tournament.save(update_fields=['status', 'updated_at'])

    return round_obj


@transaction.atomic
def mark_round_evaluated(round_obj):
    round_obj = Round.objects.select_for_update().select_related('tournament').get(id=round_obj.id)
    tournament = round_obj.tournament

    if round_obj.status != Round.STATUS_SUBMISSION_CLOSED:
        raise ValidationError({'status': 'Round must be submission_closed before evaluation.'})

    round_obj.status = Round.STATUS_EVALUATED
    round_obj.save(update_fields=['status', 'updated_at'])

    _set_tournament_finished_if_all_rounds_evaluated(tournament=tournament)

    return round_obj


@transaction.atomic
def sync_time_based_statuses(reference_time=None):
    now = reference_time or timezone.now()

    active_rounds_to_close = Round.objects.filter(
        status=Round.STATUS_ACTIVE,
        end_date__lte=now,
    )
    updated_round_ids = list(active_rounds_to_close.values_list('id', flat=True))
    if updated_round_ids:
        active_rounds_to_close.update(status=Round.STATUS_SUBMISSION_CLOSED, updated_at=now)

    running_tournaments = Tournament.objects.filter(status=Tournament.STATUS_RUNNING).prefetch_related('rounds')
    for tournament in running_tournaments:
        _set_tournament_finished_if_all_rounds_evaluated(tournament=tournament)

    return {
        'closed_round_ids': updated_round_ids,
    }
