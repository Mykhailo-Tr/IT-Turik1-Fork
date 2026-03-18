import re

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'full_name', 'phone', 'city')

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            is_active=False,
            needs_onboarding=False,
            **validated_data,
        )
        user.set_password(password)
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"http://localhost:5173/activate/{uid}/{token}"
        send_mail(
            subject='Account activation',
            message=f'Open this link to activate your account: {activation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    teams = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'role',
            'full_name',
            'phone',
            'city',
            'created_at',
            'needs_onboarding',
            'teams',
        )
        read_only_fields = ('id', 'email', 'created_at', 'needs_onboarding', 'teams')

    def get_teams(self, obj):
        return [
            {
                'id': team.id,
                'name': team.name,
            }
            for team in obj.teams.all()
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'full_name', 'phone', 'city')

    def validate_username(self, value):
        if self.instance and self.instance.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        return value

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value

    def validate(self, attrs):
        if self.instance and self.instance.needs_onboarding and 'role' not in self.initial_data:
            raise serializers.ValidationError({'role': 'Please select a role to complete Google registration.'})
        return attrs

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if user.needs_onboarding:
            user.needs_onboarding = False
            user.save(update_fields=['needs_onboarding'])
        return user
