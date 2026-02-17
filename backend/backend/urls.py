from django.contrib import admin
from django.urls import path, include
from api.views import get_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # Головний вхід в API
    path('api/hello/', get_message),
]