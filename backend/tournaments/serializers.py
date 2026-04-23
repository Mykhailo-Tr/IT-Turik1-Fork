from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from teams.models import Team
from teams.models import TeamMember

from .models import (
    JuryAssignment,
    Round,
    Submission,
    SubmissionEvaluation,
    Tournament,
    TournamentTeamRegistration,
)
from .services import ensure_round_placeholders, register_team_for_tournament


class RoundShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('id', 'position', 'name', 'start_date', 'end_date', 'status')


class TournamentPublicSerializer(serializers.ModelSerializer):
    rounds = RoundShortSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'tech_requirements',
            'must_have_requirements',
            'max_teams',
            'min_team_members',
            'rounds_count',
            'status',
            'rounds',
        )


class TournamentAdminSerializer(TournamentPublicSerializer):
    class Meta(TournamentPublicSerializer.Meta):
        read_only_fields = ('status',)

    def validate_rounds_count(self, value):
        if value < 1:
            raise serializers.ValidationError('rounds_count must be at least 1.')
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date must be greater than start_date.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tournament = Tournament(created_by=getattr(request, 'user', None), **validated_data)
        try:
            tournament.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        tournament.save()
        ensure_round_placeholders(tournament)
        return tournament

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()
        ensure_round_placeholders(instance)
        return instance


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = (
            'id',
            'tournament',
            'position',
            'name',
            'description',
            'tech_requirements',
            'must_have_requirements',
            'start_date',
            'end_date',
            'passing_count',
            'winners_count',
            'evaluation_criteria',
            'materials',
            'status',
        )
        read_only_fields = ('status',)

    def validate(self, attrs):
        instance = self.instance
        tournament = attrs.get('tournament', getattr(instance, 'tournament', None))
        position = attrs.get('position', getattr(instance, 'position', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))
        winners_count = attrs.get('winners_count', getattr(instance, 'winners_count', None))

        errors = {}

        if start_date and end_date and start_date >= end_date:
            errors['end_date'] = 'end_date must be greater than start_date.'

        if tournament and start_date and end_date:
            if start_date < tournament.start_date or end_date > tournament.end_date:
                errors['start_date'] = 'Round dates must be within tournament dates.'

            if tournament.rounds_count == 1 and (
                start_date != tournament.start_date or end_date != tournament.end_date
            ):
                errors['start_date'] = 'For single-round tournaments, round dates must match tournament dates.'

        if position is not None and position < 1:
            errors['position'] = 'position must be at least 1.'
        if tournament and position and position > tournament.rounds_count:
            errors['position'] = 'position must be less than or equal to tournament rounds_count.'

        if tournament and position and winners_count is not None and position != tournament.rounds_count:
            errors['winners_count'] = 'winners_count is allowed only for the last round.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        round_obj = Round(**validated_data)
        try:
            round_obj.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        round_obj.save()
        return round_obj

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from None
        instance.save()
        return instance


class SubmissionSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    round_name = serializers.CharField(source='round.name', read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id',
            'team',
            'round',
            'team_name',
            'round_name',
            'github_url',
            'demo_video_url',
            'demo_video_file',
            'live_demo_url',
            'description',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def _request_user(self):
        request = self.context.get('request')
        if not request:
            return None
        return request.user

    def validate(self, attrs):
        instance = self.instance
        user = self._request_user()
        team = attrs.get('team', getattr(instance, 'team', None))
        round_obj = attrs.get('round', getattr(instance, 'round', None))
        github_url = attrs.get('github_url', getattr(instance, 'github_url', ''))
        demo_video_url = attrs.get('demo_video_url', getattr(instance, 'demo_video_url', ''))
        demo_video_file = attrs.get('demo_video_file', getattr(instance, 'demo_video_file', None))

        errors = {}

        if not github_url:
            errors['github_url'] = 'github_url is required.'

        if not demo_video_url and not demo_video_file:
            errors['demo_video_url'] = 'Provide demo_video_url or demo_video_file.'

        if not team:
            errors['team'] = 'team is required.'

        if not round_obj:
            errors['round'] = 'round is required.'

        if instance is not None:
            if 'team' in attrs and attrs['team'].id != instance.team_id:
                errors['team'] = 'team cannot be changed.'
            if 'round' in attrs and attrs['round'].id != instance.round_id:
                errors['round'] = 'round cannot be changed.'

        if team and user and not TeamMember.objects.filter(team=team, user=user).exists() and team.captain_id != user.id:
            errors['team'] = 'You are not a member of this team.'

        if round_obj:
            now = timezone.now()
            if round_obj.status != Round.STATUS_ACTIVE or round_obj.end_date <= now:
                errors['round'] = 'Round is closed for submissions.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        try:
            return Submission.objects.create(created_by=getattr(request, 'user', None), **validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'team': 'Only one submission per team per round is allowed.'}) from None


class OwnSubmissionSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    round_name = serializers.CharField(source='round.name', read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id',
            'team',
            'round',
            'team_name',
            'round_name',
            'github_url',
            'demo_video_url',
            'demo_video_file',
            'live_demo_url',
            'description',
            'created_at',
            'updated_at',
        )


class CurrentTaskSerializer(serializers.ModelSerializer):
    tournament_id = serializers.IntegerField(source='tournament.id', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    deadline = serializers.DateTimeField(source='end_date', read_only=True)
    task = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Round
        fields = (
            'id',
            'tournament_id',
            'tournament_name',
            'name',
            'task',
            'deadline',
            'must_have_requirements',
            'tech_requirements',
        )


class TournamentTeamRegistrationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TournamentTeamRegistration
        fields = ('id', 'tournament', 'team', 'team_name', 'created_at')
        read_only_fields = ('id', 'tournament', 'created_at')


class TournamentTeamRegistrationCreateSerializer(serializers.Serializer):
    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), source='team')

    def save(self, **kwargs):
        request = self.context['request']
        tournament = self.context['tournament']
        team = self.validated_data['team']
        return register_team_for_tournament(
            tournament=tournament,
            team=team,
            actor=request.user,
        )


class SubmissionEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionEvaluation
        fields = (
            'id',
            'assignment',
            'score_backend',
            'score_db',
            'score_frontend',
            'score_completeness',
            'score_stability',
            'score_usability',
            'comment',
            'final_score',
            'created_at',
        )
        read_only_fields = ('final_score', 'created_at')

    def validate_assignment(self, value):
        request = self.context.get('request')
        if value.jury_id != request.user.id:
            raise serializers.ValidationError('You are not assigned to this submission.')

        qs = SubmissionEvaluation.objects.filter(assignment=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError('This submission is already evaluated.')
        return value


class JuryAssignmentSerializer(serializers.ModelSerializer):
    submission_details = SubmissionSerializer(source='submission', read_only=True)
    evaluation = SubmissionEvaluationSerializer(read_only=True)
    is_evaluated = serializers.SerializerMethodField()

    class Meta:
        model = JuryAssignment
        fields = ('id', 'submission', 'submission_details', 'evaluation', 'is_evaluated', 'created_at')

    def get_is_evaluated(self, obj):
        return hasattr(obj, 'evaluation')
