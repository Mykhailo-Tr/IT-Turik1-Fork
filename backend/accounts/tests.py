from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


@override_settings(GOOGLE_OAUTH_CLIENT_ID='test-google-client-id')
class GoogleAuthViewTests(APITestCase):
    url = reverse('google_login')
    profile_url = reverse('profile')

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_creates_user_and_returns_jwt(self, mocked_verify):
        mocked_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'email': 'new.user@example.com',
            'email_verified': True,
            'name': 'New User',
        }

        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data['onboarding_required'])

        created_user = User.objects.get(email='new.user@example.com')
        self.assertTrue(created_user.is_active)
        self.assertEqual(created_user.full_name, 'New User')
        self.assertFalse(created_user.has_usable_password())
        self.assertTrue(created_user.needs_onboarding)

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_activates_existing_user(self, mocked_verify):
        existing = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='StrongPass123!',
            is_active=False,
        )

        mocked_verify.return_value = {
            'iss': 'accounts.google.com',
            'email': 'existing@example.com',
            'email_verified': True,
            'name': 'Existing User',
        }

        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['onboarding_required'])
        existing.refresh_from_db()
        self.assertTrue(existing.is_active)

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_rejects_unverified_email(self, mocked_verify):
        mocked_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'email': 'user@example.com',
            'email_verified': False,
        }

        response = self.client.post(self.url, {'id_token': 'fake-token'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_google_login_requires_token(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_update_completes_onboarding(self):
        user = User.objects.create_user(
            username='googleuser',
            email='googleuser@example.com',
            password='StrongPass123!',
            needs_onboarding=True,
        )

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'updatedgoogleuser',
                'role': 'jury',
                'full_name': 'Updated Name',
                'phone': '+380991112233',
                'city': 'Kyiv',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, 'updatedgoogleuser')
        self.assertEqual(user.role, 'jury')
        self.assertEqual(user.full_name, 'Updated Name')
        self.assertEqual(user.phone, '+380991112233')
        self.assertEqual(user.city, 'Kyiv')
        self.assertFalse(user.needs_onboarding)

    def test_profile_delete_removes_current_user(self):
        user = User.objects.create_user(
            username='delete-me',
            email='delete-me@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user.id).exists())


class TeamApiTests(APITestCase):
    teams_url = reverse('teams')
    users_url = reverse('users')

    def setUp(self):
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='StrongPass123!',
        )
        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='StrongPass123!',
        )

    def test_create_team_assigns_captain_and_members(self):
        self.client.force_authenticate(user=self.captain)

        response = self.client.post(
            self.teams_url,
            {
                'name': 'Alpha Team',
                'email': 'alpha@example.com',
                'organization': 'T-Org',
                'contact': '+380971112233',
                'member_ids': [self.member.id],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['captain_id'], self.captain.id)
        member_ids = {member['id'] for member in response.data['members']}
        self.assertIn(self.captain.id, member_ids)
        self.assertIn(self.member.id, member_ids)

    def test_only_captain_can_update_team(self):
        self.client.force_authenticate(user=self.captain)
        create_response = self.client.post(
            self.teams_url,
            {'name': 'Beta Team', 'email': 'beta@example.com'},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        team_id = create_response.data['id']

        self.client.force_authenticate(user=self.member)
        update_response = self.client.patch(
            reverse('team_detail', kwargs={'pk': team_id}),
            {'name': 'Hacked'},
            format='json',
        )

        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_captain_can_add_and_remove_member(self):
        self.client.force_authenticate(user=self.captain)
        create_response = self.client.post(
            self.teams_url,
            {'name': 'Gamma Team', 'email': 'gamma@example.com'},
            format='json',
        )
        team_id = create_response.data['id']

        add_response = self.client.post(
            reverse('team_members', kwargs={'pk': team_id}),
            {'user_id': self.member.id},
            format='json',
        )
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)

        remove_response = self.client.delete(
            reverse('team_member_detail', kwargs={'pk': team_id, 'user_id': self.member.id})
        )
        self.assertEqual(remove_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_users_returns_current_users(self):
        self.client.force_authenticate(user=self.captain)
        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item['username'] for item in response.data}
        self.assertIn(self.captain.username, usernames)
        self.assertIn(self.member.username, usernames)

