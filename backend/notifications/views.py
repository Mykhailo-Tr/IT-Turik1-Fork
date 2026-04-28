from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List current user's notifications, newest first."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(APIView):
    """Mark a single notification as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        updated = Notification.objects.filter(
            id=pk,
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)

        if updated == 0:
            return Response(
                {'detail': 'Notification not found or already read.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'detail': 'Marked as read.'}, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    """Mark all unread notifications as read for the current user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
        return Response({'marked': count}, status=status.HTTP_200_OK)


class UnreadCountView(APIView):
    """Return the number of unread notifications (for badge display)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)
