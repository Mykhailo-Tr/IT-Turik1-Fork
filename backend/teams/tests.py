from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Team, TeamInvitation, TeamJoinRequest, TeamMember


class TeamApiTests(APITestCase):
    teams_url = reverse('teams')
    users_url = reverse('users')
    invitations_url = reverse('team_invitations')

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
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123!',
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )

    def _create_team(self, payload):
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(self.teams_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def test_create_team_creates_invitations_not_members(self):
        self.client.force_authenticate(user=self.captain)
        response = self.client.post(
            self.teams_url,
            {
                'name': 'Alpha Team',
                'email': 'alpha@example.com',
                'is_public': True,
                'organization': 'T-Org',
                'contact_telegram': '@alpha_team',
                'contact_discord': 'alpha.team',
                'member_ids': [self.member.id],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_public'])
        self.assertEqual(response.data['captain_id'], self.captain.id)
        member_ids = {member['id'] for member in response.data['members']}
        self.assertIn(self.captain.id, member_ids)
        self.assertNotIn(self.member.id, member_ids)
        self.assertEqual(response.data['contact_telegram'], 'alpha_team')
        self.assertEqual(response.data['contact_discord'], 'alpha.team')
        self.assertEqual(len(response.data['invitations']), 1)
        self.assertEqual(response.data['invitations'][0]['user']['id'], self.member.id)
        self.assertEqual(response.data['invitations'][0]['status'], TeamInvitation.STATUS_INVITED)

    def test_invited_user_can_accept_invitation(self):
        team = self._create_team(
            {
                'name': 'Beta Team',
                'email': 'beta@example.com',
                'member_ids': [self.member.id],
            }
        )

        self.client.force_authenticate(user=self.member)
        inbox_response = self.client.get(self.invitations_url)
        self.assertEqual(inbox_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox_response.data), 1)
        invitation_id = inbox_response.data[0]['id']

        accept_response = self.client.post(
            reverse('team_invitation_accept', kwargs={'invitation_id': invitation_id}),
            {},
            format='json',
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        member_ids = {member['id'] for member in accept_response.data['members']}
        self.assertIn(self.member.id, member_ids)

        self.assertFalse(TeamInvitation.objects.filter(id=invitation_id).exists())
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_invited_user_can_decline_invitation_without_becoming_member(self):
        team = self._create_team(
            {
                'name': 'Decline Team',
                'email': 'decline@example.com',
                'member_ids': [self.member.id],
            }
        )

        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.member)
        decline_response = self.client.post(
            reverse('team_invitation_decline', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )

        self.assertEqual(decline_response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, TeamInvitation.STATUS_DECLINED)
        self.assertIsNotNone(invitation.responded_at)
        self.assertFalse(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_processed_invitation_cannot_be_accepted_twice(self):
        team = self._create_team(
            {
                'name': 'Single Process Team',
                'email': 'single-process@example.com',
                'member_ids': [self.member.id],
            }
        )
        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)

        self.client.force_authenticate(user=self.member)
        first_accept = self.client.post(
            reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(first_accept.status_code, status.HTTP_200_OK)

        second_accept = self.client.post(
            reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(second_accept.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_respond_to_someone_elses_invitation(self):
        team = self._create_team(
            {
                'name': 'Ownership Team',
                'email': 'ownership@example.com',
                'member_ids': [self.member.id],
            }
        )
        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reinviting_user_resets_declined_invitation_to_invited(self):
        team = self._create_team(
            {
                'name': 'Reinvite Team',
                'email': 'reinvite@example.com',
                'member_ids': [self.member.id],
            }
        )
        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)

        self.client.force_authenticate(user=self.member)
        decline_response = self.client.post(
            reverse('team_invitation_decline', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(decline_response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, TeamInvitation.STATUS_DECLINED)
        self.assertIsNotNone(invitation.responded_at)

        self.client.force_authenticate(user=self.captain)
        reinvite_response = self.client.post(
            reverse('team_members', kwargs={'pk': team['id']}),
            {'user_id': self.member.id},
            format='json',
        )
        self.assertEqual(reinvite_response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, TeamInvitation.STATUS_INVITED)
        self.assertIsNone(invitation.responded_at)

    def test_inviting_user_with_pending_join_request_declines_that_join_request(self):
        team = self._create_team(
            {
                'name': 'Invite Beats Request Team',
                'email': 'invite-beats-request@example.com',
                'is_public': True,
            }
        )

        self.client.force_authenticate(user=self.member)
        join_response = self.client.post(
            reverse('team_join_request_create', kwargs={'pk': team['id']}),
            {},
            format='json',
        )
        self.assertEqual(join_response.status_code, status.HTTP_201_CREATED)
        join_request = TeamJoinRequest.objects.get(team_id=team['id'], user=self.member)
        self.assertEqual(join_request.status, TeamJoinRequest.STATUS_PENDING)

        self.client.force_authenticate(user=self.captain)
        invite_response = self.client.post(
            reverse('team_members', kwargs={'pk': team['id']}),
            {'user_id': self.member.id},
            format='json',
        )
        self.assertIn(invite_response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

        join_request.refresh_from_db()
        self.assertEqual(join_request.status, TeamJoinRequest.STATUS_DECLINED)
        self.assertEqual(join_request.reviewed_by_id, self.captain.id)
        self.assertIsNotNone(join_request.reviewed_at)

    def test_regular_member_cannot_see_invitations_and_join_requests(self):
        team = self._create_team(
            {
                'name': 'Gamma Team',
                'email': 'gamma@example.com',
                'member_ids': [self.member.id],
            }
        )

        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}), {}, format='json')

        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['invitations'], [])
        self.assertEqual(detail_response.data['join_requests'], [])
        member_ids = {member['id'] for member in detail_response.data['members']}
        self.assertIn(self.member.id, member_ids)
        self.assertIn(self.captain.id, member_ids)

    def test_public_team_join_request_can_be_accepted_by_captain(self):
        team = self._create_team(
            {
                'name': 'Public Team',
                'email': 'public@example.com',
                'is_public': True,
            }
        )

        self.client.force_authenticate(user=self.member)
        join_response = self.client.post(
            reverse('team_join_request_create', kwargs={'pk': team['id']}),
            {},
            format='json',
        )
        self.assertEqual(join_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.captain)
        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(detail_response.data['join_requests']), 1)
        request_id = detail_response.data['join_requests'][0]['id']
        self.assertEqual(detail_response.data['join_requests'][0]['status'], TeamJoinRequest.STATUS_PENDING)

        accept_response = self.client.post(
            reverse('team_join_request_accept', kwargs={'pk': team['id'], 'request_id': request_id}),
            {},
            format='json',
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        member_ids = {member['id'] for member in accept_response.data['members']}
        self.assertIn(self.member.id, member_ids)

    def test_member_does_not_see_join_request_status_after_becoming_member(self):
        team = self._create_team(
            {
                'name': 'Join Status Cleanup Team',
                'email': 'join-status-cleanup@example.com',
                'is_public': True,
            }
        )

        self.client.force_authenticate(user=self.member)
        join_response = self.client.post(
            reverse('team_join_request_create', kwargs={'pk': team['id']}),
            {},
            format='json',
        )
        self.assertEqual(join_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.captain)
        join_request = TeamJoinRequest.objects.get(team_id=team['id'], user=self.member)
        accept_response = self.client.post(
            reverse('team_join_request_accept', kwargs={'pk': team['id'], 'request_id': join_request.id}),
            {},
            format='json',
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.member)
        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data['is_member'])
        self.assertIsNone(detail_response.data['my_join_request_status'])

    def test_declined_invitation_is_removed_when_join_request_accepted(self):
        team = self._create_team(
            {
                'name': 'Declined Then Join Team',
                'email': 'declined-then-join@example.com',
                'is_public': True,
                'member_ids': [self.member.id],
            }
        )

        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.member)
        decline_response = self.client.post(
            reverse('team_invitation_decline', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(decline_response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, TeamInvitation.STATUS_DECLINED)

        join_response = self.client.post(
            reverse('team_join_request_create', kwargs={'pk': team['id']}),
            {},
            format='json',
        )
        self.assertIn(join_response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

        self.client.force_authenticate(user=self.captain)
        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        request_id = detail_response.data['join_requests'][0]['id']

        accept_response = self.client.post(
            reverse('team_join_request_accept', kwargs={'pk': team['id'], 'request_id': request_id}),
            {},
            format='json',
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)

        member_ids = {member['id'] for member in accept_response.data['members']}
        self.assertIn(self.member.id, member_ids)
        invitation_user_ids = {item['user']['id'] for item in accept_response.data['invitations']}
        self.assertNotIn(self.member.id, invitation_user_ids)

        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())
        self.assertFalse(TeamInvitation.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_member_never_appears_in_invitations_even_with_stale_record(self):
        team = self._create_team(
            {
                'name': 'Stale Invitation Team',
                'email': 'stale-invitation@example.com',
                'member_ids': [self.member.id],
            }
        )

        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}), {}, format='json')

        TeamInvitation.objects.create(
            team_id=team['id'],
            user=self.member,
            invited_by=self.captain,
            status=TeamInvitation.STATUS_DECLINED,
        )

        self.client.force_authenticate(user=self.captain)
        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        invitation_user_ids = {item['user']['id'] for item in detail_response.data['invitations']}
        self.assertNotIn(self.member.id, invitation_user_ids)

        self.client.force_authenticate(user=self.member)
        inbox_response = self.client.get(self.invitations_url)
        self.assertEqual(inbox_response.status_code, status.HTTP_200_OK)
        team_ids = {item['team']['id'] for item in inbox_response.data}
        self.assertNotIn(team['id'], team_ids)

    def test_member_can_leave_team_and_related_states_are_cleared(self):
        team = self._create_team(
            {
                'name': 'Leave Team',
                'email': 'leave@example.com',
                'is_public': False,
                'member_ids': [self.member.id],
            }
        )

        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.client.force_authenticate(user=self.member)
        accept_response = self.client.post(
            reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}),
            {},
            format='json',
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

        TeamInvitation.objects.create(
            team_id=team['id'],
            user=self.member,
            invited_by=self.captain,
            status=TeamInvitation.STATUS_DECLINED,
        )
        TeamJoinRequest.objects.create(
            team_id=team['id'],
            user=self.member,
            status=TeamJoinRequest.STATUS_DECLINED,
            reviewed_by=self.captain,
        )

        leave_response = self.client.post(reverse('team_leave', kwargs={'pk': team['id']}), {}, format='json')
        self.assertEqual(leave_response.status_code, status.HTTP_200_OK)
        self.assertIn('left', leave_response.data['detail'].lower())

        self.assertFalse(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())
        self.assertFalse(TeamInvitation.objects.filter(team_id=team['id'], user=self.member).exists())
        self.assertFalse(TeamJoinRequest.objects.filter(team_id=team['id'], user=self.member).exists())

        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_captain_cannot_leave_team(self):
        team = self._create_team({'name': 'Captain Team', 'email': 'captain-team@example.com'})

        self.client.force_authenticate(user=self.captain)
        leave_response = self.client.post(reverse('team_leave', kwargs={'pk': team['id']}), {}, format='json')

        self.assertEqual(leave_response.status_code, status.HTTP_400_BAD_REQUEST)
        error_text = str(leave_response.data.get('message', '')).lower()
        if not error_text and isinstance(leave_response.data.get('details'), dict):
            detail_messages = leave_response.data['details'].get('detail', [])
            if detail_messages:
                error_text = str(detail_messages[0]).lower()
        self.assertIn('captain cannot leave', error_text)
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.captain).exists())

    def test_non_member_cannot_leave_team(self):
        team = self._create_team({'name': 'Leave Restriction Team', 'email': 'leave-restrict@example.com', 'is_public': True})

        self.client.force_authenticate(user=self.other_user)
        leave_response = self.client.post(reverse('team_leave', kwargs={'pk': team['id']}), {}, format='json')

        self.assertEqual(leave_response.status_code, status.HTTP_400_BAD_REQUEST)
        error_text = str(leave_response.data.get('message', '')).lower()
        if not error_text and isinstance(leave_response.data.get('details'), dict):
            detail_messages = leave_response.data['details'].get('detail', [])
            if detail_messages:
                error_text = str(detail_messages[0]).lower()
        self.assertIn('not a team member', error_text)

    def test_private_team_not_visible_to_non_members(self):
        team = self._create_team({'name': 'Private Team', 'email': 'private@example.com', 'is_public': False})

        self.client.force_authenticate(user=self.member)
        list_response = self.client.get(self.teams_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        listed_ids = {item['id'] for item in list_response.data}
        self.assertNotIn(team['id'], listed_ids)

        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_private_teams_and_hidden_team_details(self):
        team = self._create_team(
            {
                'name': 'Admin Visibility Team',
                'email': 'admin-visibility@example.com',
                'is_public': False,
                'member_ids': [self.member.id],
            }
        )
        TeamJoinRequest.objects.create(
            team_id=team['id'],
            user=self.other_user,
            status=TeamJoinRequest.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.admin_user)
        list_response = self.client.get(self.teams_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        listed_ids = {item['id'] for item in list_response.data}
        self.assertIn(team['id'], listed_ids)

        detail_response = self.client.get(reverse('team_detail', kwargs={'pk': team['id']}))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(detail_response.data['invitations']), 1)
        self.assertEqual(detail_response.data['invitations'][0]['user']['id'], self.member.id)
        self.assertEqual(len(detail_response.data['join_requests']), 1)
        self.assertEqual(detail_response.data['join_requests'][0]['user']['id'], self.other_user.id)

    def test_captain_can_invite_additional_member_and_remove_without_confirmation(self):
        team = self._create_team({'name': 'Delta Team', 'email': 'delta@example.com'})
        self.client.force_authenticate(user=self.captain)

        invite_response = self.client.post(
            reverse('team_members', kwargs={'pk': team['id']}),
            {'user_id': self.member.id},
            format='json',
        )
        self.assertEqual(invite_response.status_code, status.HTTP_201_CREATED)
        invitation = TeamInvitation.objects.get(team_id=team['id'], user=self.member)
        self.assertEqual(invitation.status, TeamInvitation.STATUS_INVITED)

        self.client.force_authenticate(user=self.member)
        self.client.post(reverse('team_invitation_accept', kwargs={'invitation_id': invitation.id}), {}, format='json')
        self.assertTrue(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

        self.client.force_authenticate(user=self.captain)
        remove_response = self.client.delete(
            reverse('team_member_detail', kwargs={'pk': team['id'], 'user_id': self.member.id})
        )
        self.assertEqual(remove_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamMember.objects.filter(team_id=team['id'], user=self.member).exists())

    def test_non_captain_cannot_manage_members_or_join_requests(self):
        team = self._create_team({'name': 'Omega Team', 'email': 'omega@example.com', 'is_public': True})
        self.client.force_authenticate(user=self.member)

        add_response = self.client.post(
            reverse('team_members', kwargs={'pk': team['id']}),
            {'user_id': self.other_user.id},
            format='json',
        )
        self.assertEqual(add_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.other_user)
        self.client.post(reverse('team_join_request_create', kwargs={'pk': team['id']}), {}, format='json')
        join_request = TeamJoinRequest.objects.get(team_id=team['id'], user=self.other_user)

        self.client.force_authenticate(user=self.member)
        review_response = self.client.post(
            reverse('team_join_request_accept', kwargs={'pk': team['id'], 'request_id': join_request.id}),
            {},
            format='json',
        )
        self.assertEqual(review_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_returns_current_users(self):
        self.client.force_authenticate(user=self.captain)
        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item['username'] for item in response.data}
        self.assertIn(self.captain.username, usernames)
        self.assertIn(self.member.username, usernames)
        self.assertIn(self.other_user.username, usernames)

    def test_deleting_captain_cascades_to_team(self):
        team = Team.objects.create(
            name='Cascade Team',
            email='cascade-team@example.com',
            captain=self.captain,
        )
        TeamMember.objects.create(team=team, user=self.member)
        TeamInvitation.objects.create(
            team=team,
            user=self.other_user,
            invited_by=self.captain,
            status=TeamInvitation.STATUS_INVITED,
        )

        self.captain.delete()

        self.assertFalse(Team.objects.filter(id=team.id).exists())
        self.assertFalse(TeamMember.objects.filter(team_id=team.id).exists())
        self.assertFalse(TeamInvitation.objects.filter(team_id=team.id).exists())

    def test_deleting_inviter_cascades_to_invitation(self):
        inviter = User.objects.create_user(
            username='inviter',
            email='inviter@example.com',
            password='StrongPass123!',
        )
        team = Team.objects.create(
            name='Invitation Cascade Team',
            email='invitation-cascade@example.com',
            captain=self.captain,
        )
        invitation = TeamInvitation.objects.create(
            team=team,
            user=self.member,
            invited_by=inviter,
            status=TeamInvitation.STATUS_INVITED,
        )

        inviter.delete()

        self.assertTrue(Team.objects.filter(id=team.id).exists())
        self.assertFalse(TeamInvitation.objects.filter(id=invitation.id).exists())
