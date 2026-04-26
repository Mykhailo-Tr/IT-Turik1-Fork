from django.contrib import admin
from .models import CertificateTemplate, Certificate

@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_at')
    list_filter = ('is_default',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tournament_name', 'placement', 'unique_code', 'created_at')
    search_fields = ('full_name', 'tournament_name', 'unique_code')
