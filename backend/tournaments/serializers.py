from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from teams.models import Team, TeamMember
from .models import Tournament, TournamentTeam


class TournamentReadSerializer(serializers.ModelSerializer):
    registered_teams_count = serializers.SerializerMethodField()
    is_registration_open = serializers.SerializerMethodField()
    created_by_id = serializers.IntegerField(source='created_by.id', read_only=True)

    class Meta:
        model = Tournament
        fields = (
            'id',
            'title',
            'description',
            'registration_start',
            'registration_end',
            'start_date',
            'end_date',
            'max_teams',
            'min_teams',
            'rounds_count',
            'status',
            'created_by_id',
            'created_at',
            'registered_teams_count',
            'is_registration_open',
        )

    def get_registered_teams_count(self, obj):
        return obj.registered_teams_count

    def get_is_registration_open(self, obj):
        return obj.is_registration_open()


class TournamentTeamRegistrationSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        super().__init__(*args, **kwargs)

    def validate_team_id(self, value):
        try:
            team = Team.objects.select_related('captain').prefetch_related('members').get(pk=value)
        except Team.DoesNotExist:
            raise ValidationError('Team not found.')
        self._team = team
        return value

    def validate(self, attrs):
        tournament = self.tournament
        team = self._team
        request = self.context.get('request')

        if not tournament.can_accept_teams():
            if not tournament.is_registration_open():
                raise ValidationError({'message': ['Registration is not open for this tournament.']})
            raise ValidationError({'message': ['This tournament has reached the maximum number of teams.']})

        if request and request.user.id != team.captain_id:
            raise ValidationError({'team_id': ['You must be the captain of the team to register it.']})

        if TournamentTeam.objects.filter(tournament=tournament, team=team).exists():
            raise ValidationError({'team_id': ['This team is already registered for this tournament.']})

        captain_teams_in_tournament = TournamentTeam.objects.filter(
            tournament=tournament,
            team__captain_id=team.captain_id,
        )
        if captain_teams_in_tournament.exists():
            raise ValidationError(
                {'team_id': ['You already have a team registered in this tournament.']}
            )

        member_count = team.members.count()
        min_size = tournament.effective_min_teams()
        if member_count < min_size:
            raise ValidationError(
                {'team_id': [f'Team must have at least {min_size} confirmed members (currently {member_count}).']}
            )

        return attrs

    def create(self, validated_data):
        return TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self._team,
        )


class StatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Tournament.STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        super().__init__(*args, **kwargs)

    def validate_status(self, value):
        self.tournament.validate_status_transition(value)
        return value

    def save(self):
        self.tournament.status = self.validated_data['status']
        self.tournament.save(skip_auto_status=True)
        return self.tournament
