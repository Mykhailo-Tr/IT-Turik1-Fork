from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from .models import RoleActivationCode, User


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
                'role': 'team',
                'full_name': 'Updated Name',
                'phone': '+380991112233',
                'city': 'Kyiv',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, 'updatedgoogleuser')
        self.assertEqual(user.role, 'team')
        self.assertEqual(user.full_name, 'Updated Name')
        self.assertEqual(user.phone, '+380991112233')
        self.assertEqual(user.city, 'Kyiv')
        self.assertFalse(user.needs_onboarding)

    def test_profile_update_requires_redeem_code_for_restricted_google_onboarding_role(self):
        user = User.objects.create(
            username='google-restricted-no-code',
            email='google-restricted-no-code@example.com',
            needs_onboarding=True,
            is_active=True,
            role='team',
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'google-restricted-no-code-updated',
                'role': 'jury',
                'password': 'StrongerPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('redeem_code', response.data)
        user.refresh_from_db()
        self.assertEqual(user.role, 'team')
        self.assertTrue(user.needs_onboarding)

    def test_profile_update_requires_password_for_google_onboarding(self):
        user = User.objects.create(
            username='google-no-password',
            email='google-no-password@example.com',
            needs_onboarding=True,
            is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'google-no-password-updated',
                'role': 'team',
                'full_name': 'Google User',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        user.refresh_from_db()
        self.assertTrue(user.needs_onboarding)
        self.assertFalse(user.has_usable_password())

    def test_profile_update_sets_password_for_google_onboarding(self):
        user = User.objects.create(
            username='google-new-password',
            email='google-new-password@example.com',
            needs_onboarding=True,
            is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])
        role_code = RoleActivationCode.objects.create(code='ORG-GOOGLE-0001', role='organizer')

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'google-new-password-updated',
                'role': 'organizer',
                'redeem_code': role_code.code,
                'password': 'StrongerPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        role_code.refresh_from_db()
        self.assertTrue(user.check_password('StrongerPass123!'))
        self.assertEqual(user.role, 'organizer')
        self.assertTrue(role_code.is_used)
        self.assertEqual(role_code.used_by_id, user.id)
        self.assertFalse(user.needs_onboarding)

    def test_profile_update_rejects_weak_password_for_google_onboarding(self):
        user = User.objects.create(
            username='google-weak-password',
            email='google-weak-password@example.com',
            needs_onboarding=True,
            is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            self.profile_url,
            {
                'username': 'google-weak-password-updated',
                'role': 'team',
                'password': 'weakpass',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.needs_onboarding)

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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetFlowTests(APITestCase):
    request_url = reverse('password_reset_request')

    @staticmethod
    def _get_uid_and_token(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    def test_password_reset_request_sends_email(self):
        user = User.objects.create_user(
            username='reset-user',
            email='reset-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )

        response = self.client.post(self.request_url, {'email': user.email}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('reset-password', mail.outbox[0].body)
        self.assertIn(user.email, mail.outbox[0].to)

    def test_password_reset_request_rejects_nonexistent_email(self):
        response = self.client.post(self.request_url, {'email': 'missing@example.com'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_request_rejects_invalid_email_format(self):
        response = self.client.post(self.request_url, {'email': 'invalid-email'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_get_rejects_invalid_or_expired_link(self):
        user = User.objects.create_user(
            username='invalid-link-user',
            email='invalid-link-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        uid, _ = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': 'invalid-token'})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Password reset link is invalid or expired.')

    def test_password_reset_confirm_get_accepts_valid_link(self):
        user = User.objects.create_user(
            username='valid-link-user',
            email='valid-link-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset link is valid.')

    def test_password_reset_confirm_post_updates_password(self):
        user = User.objects.create_user(
            username='confirm-reset-user',
            email='confirm-reset-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        response = self.client.post(
            url,
            {
                'new_password': 'NewStrongPass123!',
                'confirm_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPass123!'))

    def test_password_reset_confirm_post_rejects_mismatched_passwords(self):
        user = User.objects.create_user(
            username='mismatch-user',
            email='mismatch-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        response = self.client.post(
            url,
            {
                'new_password': 'NewStrongPass123!',
                'confirm_password': 'DifferentPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_password_reset_confirm_post_rejects_weak_password(self):
        user = User.objects.create_user(
            username='weak-reset-user',
            email='weak-reset-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        uid, token = self._get_uid_and_token(user)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        response = self.client.post(
            url,
            {
                'new_password': 'weakpass',
                'confirm_password': 'weakpass',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class ChangePasswordFlowTests(APITestCase):
    change_url = reverse('change_password')

    def setUp(self):
        self.user = User.objects.create_user(
            username='change-password-user',
            email='change-password-user@example.com',
            password='StrongPass123!',
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        response = self.client.post(
            self.change_url,
            {
                'current_password': 'StrongPass123!',
                'new_password': 'EvenStrongerPass456!',
                'confirm_password': 'EvenStrongerPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('EvenStrongerPass456!'))

    def test_change_password_rejects_wrong_current_password(self):
        response = self.client.post(
            self.change_url,
            {
                'current_password': 'WrongPassword123!',
                'new_password': 'EvenStrongerPass456!',
                'confirm_password': 'EvenStrongerPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_password', response.data)

    def test_change_password_rejects_mismatch(self):
        response = self.client.post(
            self.change_url,
            {
                'current_password': 'StrongPass123!',
                'new_password': 'EvenStrongerPass456!',
                'confirm_password': 'AnotherPass456!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_change_password_rejects_weak_new_password(self):
        response = self.client.post(
            self.change_url,
            {
                'current_password': 'StrongPass123!',
                'new_password': 'weakpass',
                'confirm_password': 'weakpass',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RoleBasedRegistrationTests(APITestCase):
    register_url = reverse('register')
    role_codes_url = reverse('role_codes_admin')

    def test_team_member_registration_does_not_require_code(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'team-user',
                'email': 'team-user@example.com',
                'password': 'StrongPass123!',
                'role': 'team',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='team-user')
        self.assertEqual(user.role, 'team')
        self.assertFalse(user.is_superuser)

    def test_restricted_role_registration_requires_redeem_code(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'jury-user',
                'email': 'jury-user@example.com',
                'password': 'StrongPass123!',
                'role': 'jury',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('redeem_code', response.data)

    def test_restricted_role_registration_consumes_code_once(self):
        code = RoleActivationCode.objects.create(code='JURYCODE1234', role='jury')

        first_response = self.client.post(
            self.register_url,
            {
                'username': 'jury-user-1',
                'email': 'jury-user-1@example.com',
                'password': 'StrongPass123!',
                'role': 'jury',
                'redeem_code': 'JURYCODE1234',
            },
            format='json',
        )
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        code.refresh_from_db()
        self.assertTrue(code.is_used)
        self.assertEqual(code.used_by.username, 'jury-user-1')

        second_response = self.client.post(
            self.register_url,
            {
                'username': 'jury-user-2',
                'email': 'jury-user-2@example.com',
                'password': 'StrongPass123!',
                'role': 'jury',
                'redeem_code': 'JURYCODE1234',
            },
            format='json',
        )
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('redeem_code', second_response.data)

    def test_admin_role_registration_elevates_to_superuser(self):
        RoleActivationCode.objects.create(code='ADMINCODE123', role='admin')

        response = self.client.post(
            self.register_url,
            {
                'username': 'admin-user',
                'email': 'admin-user@example.com',
                'password': 'StrongPass123!',
                'role': 'admin',
                'redeem_code': 'ADMINCODE123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='admin-user')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_non_admin_cannot_manage_role_codes(self):
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=regular_user)

        response = self.client.get(self.role_codes_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_generate_codes_with_limit_of_ten_active_per_role(self):
        admin_user = User.objects.create_user(
            username='platform-admin',
            email='platform-admin@example.com',
            password='StrongPass123!',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.post(
            self.role_codes_url,
            {'role': 'jury', 'quantity': 10},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoleActivationCode.objects.filter(role='jury', is_used=False).count(), 10)

        overflow_response = self.client.post(
            self.role_codes_url,
            {'role': 'jury', 'quantity': 1},
            format='json',
        )
        self.assertEqual(overflow_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', overflow_response.data)
