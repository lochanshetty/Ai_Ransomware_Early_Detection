from django.utils import timezone
import psutil
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
        monitor_runtime.run_attack()
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


class SystemMetricsAPIView(APIView):
    """Returns system-level telemetry and component state for dashboard visuals."""

    def get(self, request):
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        components = [
            {"id": "firewall", "name": "Firewall", "status": "ACTIVE", "role": "Traffic policy enforcement", "metrics": {"blocked_rules": 12}},
            {"id": "ids", "name": "IDS/IPS", "status": "ACTIVE", "role": "Intrusion detection and prevention", "metrics": {"detections": Threat.objects.count()}},
            {"id": "threat-db", "name": "Threat DB", "status": "ACTIVE", "role": "Threat intelligence and signatures", "metrics": {"entries": 256}},
            {"id": "ml-engine", "name": "ML Engine", "status": "ACTIVE" if monitor_runtime.system_state()["monitoring"] == "running" else "STANDBY", "role": "Behavior anomaly scoring", "metrics": {"model_version": "iforest-v1"}},
            {"id": "network-monitor", "name": "Network Monitor", "status": "ACTIVE", "role": "Network telemetry sampling", "metrics": {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv}},
            {"id": "storage", "name": "Storage", "status": "ACTIVE", "role": "Log and artifact retention", "metrics": {"usage_percent": disk.percent}},
        ]
        return Response(
            {
                "status": "ok",
                "system": monitor_runtime.system_state(),
                "metrics": {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": vm.percent,
                    "disk_percent": disk.percent,
                    "network_bytes_sent": net.bytes_sent,
                    "network_bytes_recv": net.bytes_recv,
                },
                "components": components,
            },
            status=status.HTTP_200_OK,
        )
