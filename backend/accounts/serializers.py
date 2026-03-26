import re

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from .models import User


def validate_strong_password(password, user=None):
    errors = []
    if not re.search(r'[A-Z]', password):
        errors.append('Password must include at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must include at least one lowercase letter.')
    if not re.search(r'\d', password):
        errors.append('Password must include at least one digit.')
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append('Password must include at least one special character.')
    if errors:
        raise serializers.ValidationError(errors)

    validate_password(password, user=user)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'full_name', 'phone', 'city')

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError('Invalid phone number format.')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            user_for_validation = User(
                username=attrs.get('username', ''),
                email=attrs.get('email', ''),
                full_name=attrs.get('full_name', ''),
            )
            validate_strong_password(password, user=user_for_validation)
        return attrs

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
                'contact_telegram': team.contact_telegram,
                'contact_discord': team.contact_discord,
            }
            for team in obj.teams.all()
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'role', 'full_name', 'phone', 'city', 'password')

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
        if (
            self.instance
            and self.instance.needs_onboarding
            and not self.instance.has_usable_password()
            and 'password' not in self.initial_data
        ):
            raise serializers.ValidationError(
                {'password': 'Please set a password to complete Google registration.'}
            )
        password = attrs.get('password')
        if password and self.instance:
            user_for_validation = User(
                username=attrs.get('username', self.instance.username),
                email=self.instance.email,
                full_name=attrs.get('full_name', self.instance.full_name),
            )
            validate_strong_password(password, user=user_for_validation)
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        update_fields = list(validated_data.keys())
        if password:
            update_fields.append('password')
        if instance.needs_onboarding:
            instance.needs_onboarding = False
            update_fields.append('needs_onboarding')

        if update_fields:
            instance.save(update_fields=update_fields)

        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No account found with this email address.')
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:5173/reset-password/{uid}/{token}"

        send_mail(
            subject='Password reset',
            message=f'Open this link to reset your password: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError({'detail': 'Invalid password reset request.'})

        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        validate_strong_password(new_password, user=user)
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
