from django.db import models
import uuid

class CertificateTemplate(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='certificate_templates/')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other templates to not default
            CertificateTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Certificate(models.Model):
    unique_code = models.CharField(max_length=36, default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    tournament_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    placement = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.tournament_name}"

