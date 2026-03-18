# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Team(models.Model):
    """
    Модель команди.
    Чому окрема модель: Дозволяє масштабувати функціонал команд (додавати логотипи, опис) у майбутньому.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Кастомна модель користувача.
    Чому наслідуємо AbstractUser: Це зберігає стандартний функціонал Django (хешування паролів, 
    перевірки), але дозволяє додати власні поля без створення складних профілів "один-до-одного".
    """
    # Формальні ролі. Поки не впливають на логіку, але готові до розширення прав доступу.
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('team', 'Team Member'),
        ('jury', 'Jury'),
        ('organizer', 'Organizer'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team')
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Зв'язок: Багато користувачів до однієї команди.
    # on_delete=models.SET_NULL: якщо команду видалять, користувачі залишаться, але без команди.
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    # Поля created_at не потрібно додавати вручну, AbstractUser вже має date_joined.
    # Email та username вже є в AbstractUser, але робимо email унікальним обов'язково:
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username