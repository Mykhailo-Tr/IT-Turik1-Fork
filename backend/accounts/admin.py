# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Team

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Налаштування відображення користувача в адмінці.
    Чому UserAdmin: Стандартний ModelAdmin не вміє правильно хешувати паролі 
    та відображати блоки прав доступу для системних користувачів.
    """
    
    # Поля, які відображаються у списку всіх користувачів
    list_display = ('username', 'email', 'full_name', 'role', 'team', 'is_active', 'is_staff')
    
    # Фільтри збоку для швидкого пошуку
    list_filter = ('role', 'is_active', 'is_staff', 'team')
    
    # Поля, за якими працює пошук
    search_fields = ('username', 'email', 'full_name')

    # Налаштування полів при редагуванні конкретного користувача
    # fieldsets дозволяє групувати поля в логічні блоки
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('role', 'full_name', 'phone', 'city', 'team'),
        }),
    )

    # Поля, які з'являються при створенні нового користувача через адмінку
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткова інформація', {
            'fields': ('email', 'role', 'full_name', 'phone', 'city', 'team'),
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Налаштування відображення команд.
    """
    list_display = ('id', 'name', 'get_members_count')
    search_fields = ('name',)

    def get_members_count(self, obj):
        # Показуємо кількість учасників у команді прямо в списку
        return obj.members.count()
    
    get_members_count.short_description = 'Кількість учасників' 