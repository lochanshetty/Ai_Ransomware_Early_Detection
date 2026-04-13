from rest_framework import generics

from apps.api.serializers import AlertSerializer
from apps.detection.models import Alert


class AlertListCreateAPIView(generics.ListCreateAPIView):
    """Lists and creates incident alerts for operators and automation."""

    queryset = Alert.objects.select_related("threat").order_by("-created_at")
    serializer_class = AlertSerializer
