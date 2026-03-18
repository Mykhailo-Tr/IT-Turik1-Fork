import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Team, TeamMember, User
from .serializers import RegisterSerializer, TeamMemberSerializer, TeamSerializer, UserSerializer, UserUpdateSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ActivationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response({'status': 'success', 'message': 'Account activated!'}, status=status.HTTP_200_OK)

        return Response(
            {'status': 'error', 'message': 'Activation link is invalid or expired.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GoogleAuthView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def _generate_unique_username(email):
        base = re.sub(r'[^a-zA-Z0-9_]', '', email.split('@')[0]) or 'user'
        base = base[:140]
        username = base
        index = 1

        while User.objects.filter(username=username).exists():
            suffix = str(index)
            username = f"{base[:150 - len(suffix)]}{suffix}"
            index += 1

        return username

    def post(self, request):
        raw_id_token = request.data.get('id_token') or request.data.get('credential')
        if not raw_id_token:
            return Response({'detail': 'id_token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not settings.GOOGLE_OAUTH_CLIENT_ID:
            return Response({'detail': 'Google auth is not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            payload = id_token.verify_oauth2_token(
                raw_id_token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError:
            return Response({'detail': 'Invalid Google token.'}, status=status.HTTP_400_BAD_REQUEST)

        issuer = payload.get('iss')
        if issuer not in {'accounts.google.com', 'https://accounts.google.com'}:
            return Response({'detail': 'Invalid token issuer.'}, status=status.HTTP_400_BAD_REQUEST)

        if not payload.get('email_verified'):
            return Response({'detail': 'Google email is not verified.'}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get('email')
        if not email:
            return Response({'detail': 'Google account email is missing.'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = payload.get('name', '')

        user = User.objects.filter(email=email).first()
        if user is None:
            username = self._generate_unique_username(email)
            user = User.objects.create(
                username=username,
                email=email,
                full_name=full_name,
                is_active=True,
                needs_onboarding=True,
            )
            user.set_unusable_password()
            user.save()
        else:
            updated_fields = []
            if not user.is_active:
                user.is_active = True
                updated_fields.append('is_active')
            if full_name and not user.full_name:
                user.full_name = full_name
                updated_fields.append('full_name')
            if updated_fields:
                user.save(update_fields=updated_fields)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
                'onboarding_required': user.needs_onboarding,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.select_related('captain').prefetch_related('members').all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(captain=self.request.user)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.select_related('captain').prefetch_related('members').all()

    def _assert_captain(self, team):
        if team.captain_id != self.request.user.id:
            return Response({'detail': 'Only captain can modify this team.'}, status=status.HTTP_403_FORBIDDEN)
        return None

    def update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        denied = self._assert_captain(team)
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)


class TeamMemberManageView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_team(pk):
        return get_object_or_404(Team.objects.select_related('captain').prefetch_related('members'), pk=pk)

    def post(self, request, pk):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        TeamMember.objects.get_or_create(team=team, user=user)

        team.refresh_from_db()
        return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)

    def delete(self, request, pk, user_id):
        team = self._get_team(pk)
        if team.captain_id != request.user.id:
            return Response({'detail': 'Only captain can manage members.'}, status=status.HTTP_403_FORBIDDEN)

        if team.captain_id == user_id:
            return Response({'detail': 'Captain cannot be removed from team.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
        if deleted_count == 0:
            return Response({'detail': 'User is not a team member.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(full_name__icontains=search)
            )
        return queryset
