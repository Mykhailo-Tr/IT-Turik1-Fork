from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .models import User
from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer

class RegisterView(generics.CreateAPIView):
    """Ендпоінт реєстрації (відкритий для всіх)"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ActivationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            # Декодуємо ID користувача
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Перевіряємо токен. Важливо: токен одноразовий!
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save() # Обов'язково зберігаємо зміни в БД
            return Response({'status': 'success', 'message': 'Акаунт активовано!'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'error', 'message': 'Посилання недійсне або застаріло.'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Якщо запит GET - повертаємо всі дані, якщо PATCH - використовуємо серіалізатор оновлення
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user