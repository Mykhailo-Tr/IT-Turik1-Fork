from django.urls import path
from .views import GenerateCertificateView, ViewCertificateView

urlpatterns = [
    path('generate/', GenerateCertificateView.as_view(), name='generate_certificate'),
    path('view/<str:unique_code>/', ViewCertificateView.as_view(), name='view_certificate'),
]
