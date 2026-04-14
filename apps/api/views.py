from pathlib import Path
from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.system_control import stop_attack_and_reset_state
from apps.api.serializers import AlertSerializer
from apps.detection.models import Alert, SecurityLog, Threat
from apps.monitoring.services import monitor_runtime


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


class SystemStatusAPIView(APIView):
    """Returns dashboard-oriented monitoring and attack status."""

    def get(self, request):
        return Response(monitor_runtime.system_state(), status=status.HTTP_200_OK)


class SystemStartMonitoringAPIView(APIView):
    """Starts monitoring from the unified dashboard controls."""

    def post(self, request):
        monitor_runtime.start()
        print("[SYSTEM] Monitoring started")
        return Response(
            {
                "status": "ok",
                "message": "Monitoring started",
                **monitor_runtime.system_state(),
            },
            status=status.HTTP_200_OK,
        )


class SystemStopMonitoringAPIView(APIView):
    """Stops monitoring from the unified dashboard controls."""

    def post(self, request):
        monitor_runtime.stop()
        print("[SYSTEM] Monitoring stopped")
        return Response(
            {
                "status": "ok",
                "message": "Monitoring stopped",
                **monitor_runtime.system_state(),
            },
            status=status.HTTP_200_OK,
        )


class SystemRunAttackAPIView(APIView):
    """Runs simulation from dashboard controls."""

    def post(self, request):
        base_dir = Path(__file__).resolve().parents[2]
        simulate_script = base_dir / "simulate_attack.py"
        monitor_runtime.run_attack(simulate_script=simulate_script)
        print("[SYSTEM] Attack started")
        return Response(
            {
                "status": "ok",
                "message": "Attack started",
                **monitor_runtime.system_state(),
            },
            status=status.HTTP_200_OK,
        )


class SystemStopAttackAPIView(APIView):
    """Stops active simulation and reuses honeypot refresh/reset logic."""

    def post(self, request):
        result = stop_attack_and_reset_state()
        print("[SYSTEM] Attack stopped via dashboard")
        return Response(
            {
                "status": "ok",
                "message": "Attack stopped via dashboard",
                **result,
            },
            status=status.HTTP_200_OK,
        )
