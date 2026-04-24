from django.conf import settings
from django.db import models


class JuryAssignment(models.Model):
    submission = models.ForeignKey('tournaments.Submission', on_delete=models.CASCADE, related_name='jury_assignments')
    jury = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jury_assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('submission', 'jury')

    def __str__(self):
        return f'Assignment:{self.submission_id}:{self.jury_id}'


class SubmissionEvaluation(models.Model):
    assignment = models.OneToOneField(JuryAssignment, on_delete=models.CASCADE, related_name='evaluation')
    score_backend = models.PositiveSmallIntegerField(default=0)
    score_db = models.PositiveSmallIntegerField(default=0)
    score_frontend = models.PositiveSmallIntegerField(default=0)
    score_completeness = models.PositiveSmallIntegerField(default=0)
    score_stability = models.PositiveSmallIntegerField(default=0)
    score_usability = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(blank=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Evaluation:{self.assignment_id}:{self.final_score}'

    def save(self, *args, **kwargs):
        scores = [
            self.score_backend,
            self.score_db,
            self.score_frontend,
            self.score_completeness,
            self.score_stability,
            self.score_usability,
        ]
        self.final_score = sum(scores) / len(scores)
        super().save(*args, **kwargs)
