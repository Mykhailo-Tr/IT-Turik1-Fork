# project_name/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Панель адміністратора
    path('admin/', admin.site.urls),

    # Підключаємо маршрути нашого додатка користувачів
    # include() "втягує" всі URL-адреси, які ми прописали в accounts/urls.py
    path('api/accounts/', include('accounts.urls')),
    path('api/teams/', include('teams.urls')),
]