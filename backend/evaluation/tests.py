from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Team, TeamMember
from tournaments.models import Round, Submission, Tournament

from .models import JuryAssignment, SubmissionEvaluation


class JuryEvaluationCreateApiTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.jury = User.objects.create_user(
            username='jury-user',
            email='jury-user@example.com',
            password='StrongPass123!',
            role='jury',
        )
        self.other_jury = User.objects.create_user(
            username='other-jury',
            email='other-jury@example.com',
            password='StrongPass123!',
            role='jury',
        )
        self.team_user = User.objects.create_user(
            username='team-user',
            email='team-user@example.com',
            password='StrongPass123!',
            role='team',
        )
        self.team = Team.objects.create(
            name='Eval Team',
            email='eval-team@example.com',
            captain=self.team_user,
        )
        TeamMember.objects.create(team=self.team, user=self.team_user)

        self.tournament = Tournament.objects.create(
            name='Main Tournament',
            description='Main',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=3),
            status=Tournament.STATUS_RUNNING,
        )
        self.other_tournament = Tournament.objects.create(
            name='Other Tournament',
            description='Other',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=3),
            status=Tournament.STATUS_RUNNING,
        )

        self.round_obj = Round.objects.create(
            tournament=self.tournament,
            name='Round 1',
            criteria=[
                {'id': 'backend', 'name': 'Backend', 'max_score': 10},
                {'id': 'db', 'name': 'Database', 'max_score': 10},
            ],
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=2),
            status=Round.STATUS_SUBMISSION_CLOSED,
        )
        self.other_round = Round.objects.create(
            tournament=self.other_tournament,
            name='Round 1',
            criteria=[{'id': 'ux', 'name': 'UX', 'max_score': 10}],
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=2),
            status=Round.STATUS_SUBMISSION_CLOSED,
        )
        self.submission = Submission.objects.create(
            team=self.team,
            round=self.round_obj,
            github_url='https://github.com/example/repo',
            demo_video_url='https://youtube.com/watch?v=test',
        )
        self.other_submission = Submission.objects.create(
            team=self.team,
            round=self.other_round,
            github_url='https://github.com/example/repo-2',
            demo_video_url='https://youtube.com/watch?v=test2',
        )
        self.assignment = JuryAssignment.objects.create(submission=self.submission, jury=self.jury)
        self.other_assignment = JuryAssignment.objects.create(submission=self.other_submission, jury=self.other_jury)
        self.url = reverse('jury_evaluate_create')

    def _valid_scores(self):
        return [
            {'criterion_id': 'backend', 'score': 10},
            {'criterion_id': 'db', 'score': 8},
        ]

    def test_create_evaluation_success_with_matching_tournament_id(self):
        self.client.force_authenticate(user=self.jury)
        payload = {
            'tournament_id': self.tournament.id,
            'assignment': self.assignment.id,
            'scores': self._valid_scores(),
            'comment': 'Excellent work!',
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SubmissionEvaluation.objects.filter(assignment=self.assignment).exists())
        self.assertNotIn('tournament_id', response.data)

    def test_create_evaluation_fails_when_tournament_id_is_for_other_tournament(self):
        self.client.force_authenticate(user=self.jury)
        payload = {
            'tournament_id': self.other_tournament.id,
            'assignment': self.assignment.id,
            'scores': self._valid_scores(),
            'comment': 'Mismatch tournament',
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data.get('details', response.data)
        self.assertIn('tournament_id', details)

    def test_create_evaluation_fails_when_tournament_id_missing(self):
        self.client.force_authenticate(user=self.jury)
        payload = {
            'assignment': self.assignment.id,
            'scores': self._valid_scores(),
            'comment': 'No tournament id',
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data.get('details', response.data)
        self.assertIn('tournament_id', details)

    def test_create_evaluation_fails_for_not_assigned_jury(self):
        self.client.force_authenticate(user=self.jury)
        payload = {
            'tournament_id': self.other_tournament.id,
            'assignment': self.other_assignment.id,
            'scores': [{'criterion_id': 'ux', 'score': 9}],
            'comment': 'Not assigned',
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data.get('details', response.data)
        self.assertIn('assignment', details)

    def test_create_evaluation_preserves_existing_scores_validation(self):
        self.client.force_authenticate(user=self.jury)
        payload = {
            'tournament_id': self.tournament.id,
            'assignment': self.assignment.id,
            'scores': [{'criterion_id': 'backend', 'score': 10}],
            'comment': 'Missing one criterion',
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data.get('details', response.data)
        self.assertIn('scores', details)
