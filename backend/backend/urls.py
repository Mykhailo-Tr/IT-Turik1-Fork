from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/tournaments/', include('tournaments.urls')),
    path("api/evaluation/", include("evaluation.urls")),
]