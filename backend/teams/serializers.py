import re

from rest_framework import serializers

from accounts.models import User

from .models import Team, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role')


class TeamSerializer(serializers.ModelSerializer):
    captain_id = serializers.IntegerField(source='captain.id', read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
    )
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = (
            'id',
            'name',
            'email',
            'captain_id',
            'organization',
            'contact_telegram',
            'contact_discord',
            'members',
            'member_ids',
        )

    def validate_contact_telegram(self, value):
        normalized = value.strip().lstrip('@')
        if not normalized:
            return ''

        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', normalized):
            raise serializers.ValidationError(
                'Telegram username must be 5-32 chars, start with a letter, and contain only letters, digits, or _.'
            )

        return normalized

    def validate_contact_discord(self, value):
        normalized = value.strip().lstrip('@')
        if not normalized:
            return ''

        if not re.fullmatch(r'(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?', normalized):
            raise serializers.ValidationError(
                'Discord username must be 2-32 chars and may contain letters, digits, ".", "_" and optional #1234.'
            )

        return normalized

    def validate_member_ids(self, value):
        if not value:
            return []

        unique_ids = sorted(set(value))
        existing_ids = set(User.objects.filter(id__in=unique_ids).values_list('id', flat=True))
        missing_ids = [user_id for user_id in unique_ids if user_id not in existing_ids]
        if missing_ids:
            raise serializers.ValidationError(f'Users not found: {missing_ids}')
        return unique_ids

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        captain = validated_data.pop('captain')

        team = Team.objects.create(captain=captain, **validated_data)
        TeamMember.objects.get_or_create(team=team, user=captain)

        for user in User.objects.filter(id__in=member_ids).exclude(id=captain.id):
            TeamMember.objects.get_or_create(team=team, user=user)

        return team

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        instance = super().update(instance, validated_data)

        if member_ids is not None:
            target_ids = set(member_ids)
            target_ids.add(instance.captain_id)
            current_ids = set(instance.members.values_list('id', flat=True))

            to_add = target_ids - current_ids
            to_remove = current_ids - target_ids

            for user in User.objects.filter(id__in=to_add):
                TeamMember.objects.get_or_create(team=instance, user=user)

            TeamMember.objects.filter(team=instance, user_id__in=to_remove).delete()

        return instance
