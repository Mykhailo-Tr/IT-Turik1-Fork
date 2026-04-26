from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Team, TeamMember
from .models import Tournament, Round, Submission, TournamentTeamRegistration


class TournamentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='StrongPass123!',
        )
        self.team = Team.objects.create(
            name='Test Team',
            email='test@example.com',
            captain=self.captain,
        )
        TeamMember.objects.create(team=self.team, user=self.captain)

        self.tournament_data = {
            'name': 'Dev Tournament',
            'description': 'Test description',
            'start_date': timezone.now() + timezone.timedelta(days=1),
            'end_date': timezone.now() + timezone.timedelta(days=10),
        }

    def test_admin_can_create_tournament(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Round.objects.count(), 0)

    def test_non_admin_cannot_create_tournament(self):
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_manage_create')
        response = self.client.post(url, self.tournament_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_update_tournament(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_manage_update', kwargs={'pk': tournament.id})
        response = self.client.patch(url, {'name': 'Hacked Name'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('tournament_start_registration', kwargs={'pk': tournament.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tournament.refresh_from_db()
        self.assertEqual(tournament.status, Tournament.STATUS_REGISTRATION)

    def test_team_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TournamentTeamRegistration.objects.filter(tournament=tournament, team=self.team).exists())

    def test_round_management(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds')
        
        round_data = {
            'tournament': tournament.id,
            'position': 3,
            'name': 'Extra Round',
            'start_date': self.tournament_data['start_date'],
            'end_date': self.tournament_data['end_date'],
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        round_data['position'] = 1
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submission_creation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        
        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
            'team': self.team.id,
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Test submission',
        }
        response = self.client.post(url, submission_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

        # Test duplicate submission fails
        response = self.client.post(url, submission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        # We check that there are some details about the error, 
        # without strictly requiring 'non_field_errors' or 'team' key
        self.assertTrue(response.data.get('details'))

    def test_submission_requires_team_tournament_registration(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(hours=1),
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('submissions')
        submission_data = {
            'team': self.team.id,
            'round': round_obj.id,
            'github_url': 'https://github.com/test/repo',
            'demo_video_url': 'https://youtube.com/test',
            'description': 'Unregistered team submission',
        }
        response = self.client.post(url, submission_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')
        self.assertIn('team', response.data['details'])

    def test_registration_limit_reached(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            max_teams=1,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(tournament=tournament, team=self.team)
        
        other_user = User.objects.create_user(username='other', email='other@example.com', password='StrongPass123!')
        other_team = Team.objects.create(name='Other Team', email='other@example.com', captain=other_user)
        
        self.client.force_authenticate(user=other_user)
        url = reverse('tournament_register_team', kwargs={'pk': tournament.id})
        response = self.client.post(url, {'team_id': other_team.id}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tournament', response.data['details'])

    def test_registration_fails_when_team_already_in_another_active_tournament(self):
        active_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=active_tournament,
            team=self.team,
            created_by=self.captain,
        )

        target_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': target_tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['details'].get('team'),
            'This team is already participating in another tournament.',
        )

    def test_registration_fails_when_team_shares_members_with_active_tournament_team(self):
        shared_user = User.objects.create_user(
            username='shared-member',
            email='shared-member@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=shared_user)

        other_captain = User.objects.create_user(
            username='other-captain',
            email='other-captain@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Team',
            email='other-team@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)
        TeamMember.objects.create(team=other_team, user=shared_user)

        active_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        TournamentTeamRegistration.objects.create(
            tournament=active_tournament,
            team=other_team,
            created_by=other_captain,
        )

        target_tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_register_team', kwargs={'pk': target_tournament.id})
        response = self.client.post(url, {'team_id': self.team.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('team', response.data['details'])
        self.assertIn(shared_user.email, response.data['details']['team'])

    def test_eligible_teams_returns_only_captain_teams_with_members_count(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_REGISTRATION,
            **self.tournament_data
        )
        other_captain = User.objects.create_user(
            username='another-captain',
            email='another-captain@example.com',
            password='StrongPass123!',
        )
        other_team = Team.objects.create(
            name='Other Captain Team',
            email='other-captain-team@example.com',
            captain=other_captain,
        )
        TeamMember.objects.create(team=other_team, user=other_captain)

        extra_member = User.objects.create_user(
            username='extra-member',
            email='extra-member@example.com',
            password='StrongPass123!',
        )
        TeamMember.objects.create(team=self.team, user=extra_member)

        self.client.force_authenticate(user=self.captain)
        url = reverse('tournament_eligible_teams', kwargs={'pk': tournament.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.team.id)
        self.assertEqual(response.data[0]['name'], self.team.name)
        self.assertEqual(response.data[0]['members_count'], 3)

    def test_sync_time_based_statuses(self):
        from .services import sync_time_based_statuses
        
        tournament = Tournament.objects.create(
            created_by=self.admin,
            status=Tournament.STATUS_RUNNING,
            **self.tournament_data
        )
        round_obj = Round.objects.create(
            tournament=tournament,
            position=1,
            status=Round.STATUS_ACTIVE,
            start_date=timezone.now() - timezone.timedelta(days=2),
            end_date=timezone.now() - timezone.timedelta(days=1),
        )
        
        sync_time_based_statuses()
        round_obj.refresh_from_db()
        self.assertEqual(round_obj.status, Round.STATUS_SUBMISSION_CLOSED)

    def test_round_dates_validation(self):
        tournament = Tournament.objects.create(
            created_by=self.admin,
            **self.tournament_data
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse('rounds')
        
        round_data = {
            'tournament': tournament.id,
            'position': 1,
            'name': 'Invalid Round',
            'start_date': tournament.start_date - timezone.timedelta(days=1),
            'end_date': tournament.end_date,
        }
        response = self.client.post(url, round_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data['details'])
