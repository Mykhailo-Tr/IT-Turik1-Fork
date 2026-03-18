# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ActivationView, UserProfileView

urlpatterns = [
    # JWT Auth
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Повертає access та refresh токени
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration & Profile
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]