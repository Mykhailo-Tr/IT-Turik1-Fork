from django.contrib import admin
from django.urls import path
from api.views import get_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/', get_message),
]