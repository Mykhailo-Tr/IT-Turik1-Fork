from rest_framework import serializers
from .models import JuryAssignment, SubmissionEvaluation
from tournaments.serializers import SubmissionSerializer


class RoundAssignmentRequestSerializer(serializers.Serializer):
    k = serializers.IntegerField(required=False, default=2, min_value=1)


class SubmissionEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionEvaluation
        fields = (
            'id',
            'assignment',
            'score_backend',
            'score_db',
            'score_frontend',
            'score_completeness',
            'score_stability',
            'score_usability',
            'comment',
            'final_score',
            'created_at',
        )
        read_only_fields = ('final_score', 'created_at')

    def validate_assignment(self, value):
        request = self.context.get('request')
        if value.jury_id != request.user.id:
            raise serializers.ValidationError('You are not assigned to this submission.')

        qs = SubmissionEvaluation.objects.filter(assignment=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError('This submission is already evaluated.')
        return value


class JuryAssignmentSerializer(serializers.ModelSerializer):
    submission_details = SubmissionSerializer(source='submission', read_only=True)
    evaluation = SubmissionEvaluationSerializer(read_only=True)
    is_evaluated = serializers.SerializerMethodField()

    class Meta:
        model = JuryAssignment
        fields = ('id', 'submission', 'submission_details', 'evaluation', 'is_evaluated', 'created_at')

    def get_is_evaluated(self, obj):
        return hasattr(obj, 'evaluation')
