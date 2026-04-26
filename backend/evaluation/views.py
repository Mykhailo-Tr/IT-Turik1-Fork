from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tournaments.models import Round
from tournaments.permissions import IsJuryPermission, IsPlatformAdminPermission
from .services import assign_submissions_to_jury, try_auto_evaluate_round

from .models import JuryAssignment, SubmissionEvaluation
from .serializers import (
    JuryAssignmentSerializer,
    RoundAssignmentRequestSerializer,
    SubmissionEvaluationSerializer,
)


class JuryAssignmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsJuryPermission]
    serializer_class = JuryAssignmentSerializer

    def get_queryset(self):
        return JuryAssignment.objects.filter(jury=self.request.user).select_related(
            'submission', 'submission__team', 'submission__round', 'submission__round__tournament'
        )


class JuryEvaluationCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsJuryPermission]
    serializer_class = SubmissionEvaluationSerializer

    def perform_create(self, serializer):
        serializer.save()
        round_obj = serializer.instance.assignment.submission.round
        try_auto_evaluate_round(round_obj)


class JuryEvaluationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsJuryPermission]
    serializer_class = SubmissionEvaluationSerializer
    lookup_field = 'assignment_id'

    def get_queryset(self):
        return SubmissionEvaluation.objects.filter(assignment__jury=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        round_obj = serializer.instance.assignment.submission.round
        try_auto_evaluate_round(round_obj)


class AdminRoundAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdminPermission]

    def post(self, request, pk):
        round_obj = get_object_or_404(Round, pk=pk)
        request_serializer = RoundAssignmentRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        k = request_serializer.validated_data['k']
        assign_submissions_to_jury(round_obj, k=k)
        return Response({'status': 'Assignments created.'}, status=status.HTTP_201_CREATED)
