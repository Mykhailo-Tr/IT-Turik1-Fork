# accounts/serializers.py
import re
from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для реєстрації з усіма полями моделі.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'full_name', 'phone', 'city')

    def validate_phone(self, value):
        # Перевірка формату: дозволяємо цифри, плюси та довжину 10-15 символів
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Некоректний формат номера телефону.")
        return value

    def create(self, validated_data):
        # Витягуємо пароль, щоб створити користувача через create_user (для хешування)
        password = validated_data.pop('password')
        user = User.objects.create_user(
            is_active=False, # Користувач неактивний до підтвердження пошти
            **validated_data
        )
        user.set_password(password)
        user.save()

        # Логіка активації (UID + Token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        activation_link = f"http://localhost:5173/activate/{uid}/{token}"
        send_mail(
            subject='Активація акаунту',
            message=f'Для активації перейди за посиланням: {activation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """Серіалізатор профілю (включаючи створену дату)"""
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'full_name', 'phone', 'city', 'team', 'created_at')
        read_only_fields = ('id', 'username', 'email', 'role', 'created_at')

class UserUpdateSerializer(serializers.ModelSerializer):
    """Серіалізатор лише для полів, які дозволено редагувати в профілі"""
    class Meta:
        model = User
        fields = ('full_name', 'phone', 'city')

    def validate_phone(self, value):
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Некоректний формат телефону.")
        return value