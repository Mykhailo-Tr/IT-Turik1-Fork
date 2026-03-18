from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


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
