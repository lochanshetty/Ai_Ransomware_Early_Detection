from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers import AlertSerializer
from apps.detection.models import Alert, SecurityLog, Threat


class AlertListCreateAPIView(generics.ListCreateAPIView):
    """Lists and creates incident alerts for operators and automation."""

    queryset = Alert.objects.select_related("threat").order_by("-created_at")
    serializer_class = AlertSerializer


class HealthCheckAPIView(APIView):
    """Basic backend health endpoint for frontend startup diagnostics."""

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "CRDS backend",
                "timestamp": timezone.now().isoformat(),
                "counts": {
                    "logs": SecurityLog.objects.count(),
                    "threats": Threat.objects.count(),
                    "alerts": Alert.objects.count(),
                },
            }
        )
