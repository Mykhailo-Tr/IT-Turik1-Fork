from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Team, TeamMember
from .models import Tournament, TournamentTeam


class TournamentModelCleanTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True,
        )

    def _make(self, **overrides):
        defaults = {
            'title': 'T',
            'created_by': self.admin,
        }
        defaults.update(overrides)
        return Tournament(**defaults)

    def test_min_teams_below_floor_raises(self):
        t = self._make(min_teams=1)
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('min_teams', ctx.exception.message_dict)

    def test_min_teams_at_floor_ok(self):
        t = self._make(min_teams=2)
        t.clean()

    def test_rounds_count_zero_raises(self):
        t = self._make(rounds_count=0)
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('rounds_count', ctx.exception.message_dict)

    def test_rounds_count_one_ok(self):
        t = self._make(rounds_count=1)
        t.clean()

    def test_max_teams_zero_raises(self):
        t = self._make(max_teams=0)
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('max_teams', ctx.exception.message_dict)

    def test_max_teams_none_ok(self):
        t = self._make(max_teams=None)
        t.clean()

    def test_registration_start_after_end_raises(self):
        now = timezone.now()
        t = self._make(registration_start=now + timedelta(days=2), registration_end=now + timedelta(days=1))
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('registration_end', ctx.exception.message_dict)

    def test_start_after_end_raises(self):
        now = timezone.now()
        t = self._make(start_date=now + timedelta(days=5), end_date=now + timedelta(days=3))
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('end_date', ctx.exception.message_dict)

    def test_registration_end_after_start_date_raises(self):
        now = timezone.now()
        t = self._make(
            registration_end=now + timedelta(days=4),
            start_date=now + timedelta(days=3),
            end_date=now + timedelta(days=10),
        )
        with self.assertRaises(DjangoValidationError) as ctx:
            t.clean()
        self.assertIn('registration_end', ctx.exception.message_dict)

    def test_valid_dates_ok(self):
        now = timezone.now()
        t = self._make(
            registration_start=now + timedelta(days=1),
            registration_end=now + timedelta(days=3),
            start_date=now + timedelta(days=5),
            end_date=now + timedelta(days=10),
        )
        t.clean()


class TournamentStatusTransitionModelTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True,
        )

    def _create_tournament(self, **overrides):
        defaults = {
            'title': 'T',
            'created_by': self.admin,
            'status': Tournament.STATUS_DRAFT,
        }
        defaults.update(overrides)
        t = Tournament(**defaults)
        t.save(skip_auto_status=True)
        return t

    def test_draft_to_registration_ok(self):
        t = self._create_tournament()
        t.validate_status_transition('registration')

    def test_draft_to_running_ok(self):
        t = self._create_tournament()
        t.validate_status_transition('running')

    def test_draft_to_finished_raises(self):
        t = self._create_tournament()
        with self.assertRaises(DjangoValidationError):
            t.validate_status_transition('finished')

    def test_registration_to_running_ok(self):
        t = self._create_tournament(status=Tournament.STATUS_REGISTRATION)
        t.validate_status_transition('running')

    def test_registration_to_draft_raises(self):
        t = self._create_tournament(status=Tournament.STATUS_REGISTRATION)
        with self.assertRaises(DjangoValidationError):
            t.validate_status_transition('draft')

    def test_running_to_finished_ok(self):
        t = self._create_tournament(status=Tournament.STATUS_RUNNING)
        t.validate_status_transition('finished')

    def test_finished_to_any_raises(self):
        t = self._create_tournament(status=Tournament.STATUS_FINISHED)
        for s in ('draft', 'registration', 'running'):
            with self.assertRaises(DjangoValidationError):
                t.validate_status_transition(s)


class TournamentAutoStatusTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True,
        )

    def test_auto_advance_draft_to_registration(self):
        past = timezone.now() - timedelta(hours=1)
        future = timezone.now() + timedelta(days=5)
        t = Tournament(
            title='T', created_by=self.admin,
            registration_start=past, registration_end=future,
            start_date=future + timedelta(days=1),
            end_date=future + timedelta(days=5),
            status=Tournament.STATUS_DRAFT,
        )
        t.save()
        self.assertEqual(t.status, Tournament.STATUS_REGISTRATION)

    def test_auto_advance_draft_to_running_no_reg_window(self):
        past = timezone.now() - timedelta(hours=1)
        t = Tournament(
            title='T', created_by=self.admin,
            start_date=past,
            end_date=timezone.now() + timedelta(days=5),
            status=Tournament.STATUS_DRAFT,
        )
        t.save()
        self.assertEqual(t.status, Tournament.STATUS_RUNNING)

    def test_no_auto_advance_when_skip_flag(self):
        past = timezone.now() - timedelta(hours=1)
        t = Tournament(
            title='T', created_by=self.admin,
            registration_start=past,
            status=Tournament.STATUS_DRAFT,
        )
        t.save(skip_auto_status=True)
        self.assertEqual(t.status, Tournament.STATUS_DRAFT)


class TournamentHelperTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True,
        )

    def _create_tournament(self, **overrides):
        defaults = {
            'title': 'T',
            'created_by': self.admin,
            'status': Tournament.STATUS_DRAFT,
        }
        defaults.update(overrides)
        t = Tournament(**defaults)
        t.save(skip_auto_status=True)
        return t

    def test_is_registration_open_true(self):
        now = timezone.now()
        t = self._create_tournament(
            status=Tournament.STATUS_REGISTRATION,
            registration_start=now - timedelta(hours=1),
            registration_end=now + timedelta(hours=1),
        )
        self.assertTrue(t.is_registration_open())

    def test_is_registration_open_false_wrong_status(self):
        now = timezone.now()
        t = self._create_tournament(
            status=Tournament.STATUS_DRAFT,
            registration_start=now - timedelta(hours=1),
            registration_end=now + timedelta(hours=1),
        )
        self.assertFalse(t.is_registration_open())

    def test_effective_min_teams_clamps(self):
        t = self._create_tournament(min_teams=5)
        self.assertEqual(t.effective_min_teams(), 5)

    def test_effective_min_teams_floor(self):
        t = self._create_tournament(min_teams=2)
        self.assertEqual(t.effective_min_teams(), 2)

    def test_can_accept_teams_capacity_full(self):
        now = timezone.now()
        t = self._create_tournament(
            status=Tournament.STATUS_REGISTRATION,
            registration_start=now - timedelta(hours=1),
            registration_end=now + timedelta(hours=1),
            max_teams=1,
        )
        captain = User.objects.create_user(username='cap', email='cap@test.com', password='Pass1234!')
        team = Team.objects.create(name='Team1', email='t@t.com', captain=captain)
        TournamentTeam.objects.create(tournament=t, team=team)
        self.assertFalse(t.can_accept_teams())


class TournamentRegistrationAPITests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True, is_superuser=True,
        )
        self.captain = User.objects.create_user(
            username='captain', email='captain@test.com', password='Pass1234!',
        )
        self.member1 = User.objects.create_user(
            username='member1', email='member1@test.com', password='Pass1234!',
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@test.com', password='Pass1234!',
        )

        self.team = Team.objects.create(name='Alpha', email='alpha@t.com', captain=self.captain)
        TeamMember.objects.create(team=self.team, user=self.captain)
        TeamMember.objects.create(team=self.team, user=self.member1)

        now = timezone.now()
        self.tournament = Tournament(
            title='Cup',
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            registration_start=now - timedelta(hours=1),
            registration_end=now + timedelta(hours=5),
            start_date=now + timedelta(days=2),
            end_date=now + timedelta(days=5),
            min_teams=2,
        )
        self.tournament.save(skip_auto_status=True)
        self.register_url = reverse('tournament_register', kwargs={'pk': self.tournament.pk})

    def test_register_team_success(self):
        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TournamentTeam.objects.filter(tournament=self.tournament, team=self.team).exists())
        self.assertEqual(resp.data['registered_teams_count'], 1)

    def test_register_when_closed_fails(self):
        self.tournament.status = Tournament.STATUS_DRAFT
        self.tournament.save(skip_auto_status=True)
        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_captain_cannot_register(self):
        self.client.force_authenticate(user=self.other_user)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_team_registration_fails(self):
        TournamentTeam.objects.create(tournament=self.tournament, team=self.team)
        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_captain_with_another_team_fails(self):
        other_team = Team.objects.create(name='Beta', email='beta@t.com', captain=self.captain)
        TeamMember.objects.create(team=other_team, user=self.captain)
        TeamMember.objects.create(team=other_team, user=self.member1)
        TournamentTeam.objects.create(tournament=self.tournament, team=other_team)

        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_below_min_size_fails(self):
        small_captain = User.objects.create_user(
            username='smallcap', email='smallcap@test.com', password='Pass1234!',
        )
        small_team = Team.objects.create(name='Solo', email='solo@t.com', captain=small_captain)
        TeamMember.objects.create(team=small_team, user=small_captain)

        self.client.force_authenticate(user=small_captain)
        resp = self.client.post(self.register_url, {'team_id': small_team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_teams_reached_fails(self):
        self.tournament.max_teams = 1
        self.tournament.save(skip_auto_status=True)

        filler_captain = User.objects.create_user(
            username='filler', email='filler@test.com', password='Pass1234!',
        )
        filler_team = Team.objects.create(name='Filler', email='filler@t.com', captain=filler_captain)
        TournamentTeam.objects.create(tournament=self.tournament, team=filler_team)

        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_fails(self):
        resp = self.client.post(self.register_url, {'team_id': self.team.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_team_fails(self):
        self.client.force_authenticate(user=self.captain)
        resp = self.client.post(self.register_url, {'team_id': 99999}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class TournamentStatusTransitionAPITests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Pass1234!',
            role='admin', is_staff=True, is_superuser=True,
        )
        self.user = User.objects.create_user(
            username='user', email='user@test.com', password='Pass1234!',
        )
        self.tournament = Tournament(
            title='Cup',
            created_by=self.admin,
            status=Tournament.STATUS_DRAFT,
        )
        self.tournament.save(skip_auto_status=True)
        self.url = reverse('tournament_status', kwargs={'pk': self.tournament.pk})

    def test_admin_can_transition_draft_to_registration(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self.url, {'status': 'registration'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.status, Tournament.STATUS_REGISTRATION)

    def test_admin_can_transition_draft_to_running(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self.url, {'status': 'running'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.status, Tournament.STATUS_RUNNING)

    def test_invalid_transition_fails(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self.url, {'status': 'finished'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_transition(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(self.url, {'status': 'registration'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_fails(self):
        resp = self.client.post(self.url, {'status': 'registration'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
