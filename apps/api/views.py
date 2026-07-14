import os
from pathlib import Path

from django.utils import timezone
import psutil
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.system_control import stop_attack_and_reset_state
from apps.api.serializers import AlertSerializer
from apps.detection.models import Alert, FeatureRecord, HashRecord, ModelPrediction, ProcessRecord, SecurityLog, Threat
from apps.detection.services.model_loader import model_loader
from apps.monitoring.services import monitor_runtime


def _system_disk_usage():
    """Return disk usage for the primary system volume (Windows/Linux/macOS)."""
    if os.name == "nt":
        return psutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\")
    return psutil.disk_usage("/")


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
        disk = _system_disk_usage()
        net = psutil.net_io_counters()
        model_info = model_loader.model_info
        ml_ready = model_loader.is_ready
        hash_count = HashRecord.objects.count()
        components = [
            {
                "id": "ids",
                "name": "IDS/IPS",
                "status": "ACTIVE" if monitor_runtime.system_state()["monitoring"] == "running" else "STANDBY",
                "role": "Intrusion detection and prevention",
                "metrics": {"detections": Threat.objects.count(), "alerts": Alert.objects.count()},
            },
            {
                "id": "threat-db",
                "name": "Threat DB",
                "status": "ACTIVE",
                "role": "Threat intelligence and hash signatures",
                "metrics": {"entries": hash_count, "blacklist": HashRecord.objects.filter(label="blacklist").count()},
            },
            {
                "id": "ml-engine",
                "name": "ML Engine",
                "status": "ACTIVE" if ml_ready else "DEGRADED",
                "role": "Hybrid AI + behavioral scoring",
                "metrics": {
                    "model_version": model_info.get("name", "not_loaded"),
                    "model_type": model_info.get("type", "unknown"),
                    "metrics": model_info.get("metrics", {}),
                },
            },
            {
                "id": "network-monitor",
                "name": "Network Monitor",
                "status": "ACTIVE",
                "role": "Network telemetry sampling",
                "metrics": {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv},
            },
            {
                "id": "storage",
                "name": "Storage",
                "status": "ACTIVE",
                "role": "Log and artifact retention",
                "metrics": {"usage_percent": disk.percent, "logs": SecurityLog.objects.count()},
            },
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


class ModelInfoAPIView(APIView):
    """Returns active ML model metadata and registry summary."""

    def get(self, request):
        registry = {}
        registry_path = Path(model_loader.registry_path)
        if registry_path.exists():
            import json
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        return Response(
            {
                "status": "ok",
                "loaded": model_loader.is_ready,
                "active_model": registry.get("active_model"),
                "model_info": model_loader.model_info,
                "registry": registry,
            },
            status=status.HTTP_200_OK,
        )


class DetectionExplainAPIView(APIView):
    """Explainable AI endpoint for a specific threat detection."""

    def get(self, request, threat_id: int):
        threat = Threat.objects.select_related("security_log").filter(id=threat_id).first()
        if not threat:
            return Response({"detail": "Threat not found"}, status=status.HTTP_404_NOT_FOUND)

        log = threat.security_log
        feature_record = FeatureRecord.objects.filter(security_log=log).order_by("-created_at").first()
        prediction = ModelPrediction.objects.filter(security_log=log).order_by("-created_at").first()
        process_record = ProcessRecord.objects.filter(security_log=log).order_by("-created_at").first()
        payload = threat.analysis_payload or {}

        return Response(
            {
                "status": "ok",
                "threat_id": threat.id,
                "threat_level": threat.threat_level,
                "threat_type": threat.threat_type,
                "confidence_score": threat.confidence_score,
                "reason": threat.reason,
                "message": threat.message,
                "explanation": payload.get("explanation") or threat.reason,
                "ai_score": payload.get("ai_score"),
                "rule_score": payload.get("rule_score"),
                "feature_importance": payload.get("feature_importance", {}),
                "rule_matches": payload.get("rule_matches", []),
                "mitre_techniques": payload.get("mitre_techniques", []),
                "feature_vector": feature_record.feature_vector if feature_record else {},
                "feature_names": feature_record.feature_names if feature_record else [],
                "process": process_record.metadata if process_record else {},
                "prediction": {
                    "model_name": prediction.model_name if prediction else None,
                    "model_version": prediction.model_version if prediction else None,
                    "ai_score": prediction.ai_score if prediction else None,
                    "rule_score": prediction.rule_score if prediction else None,
                    "total_score": prediction.total_score if prediction else None,
                    "latency_ms": prediction.prediction_latency_ms if prediction else None,
                },
                "response_actions": payload.get("response_actions", []),
            },
            status=status.HTTP_200_OK,
        )


class LiveEventsAPIView(APIView):
    """Returns recent security events with detection outcomes for dashboard polling."""

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 50)), 200)
        logs = SecurityLog.objects.order_by("-created_at")[:limit]
        events = []
        for log in logs:
            threat = Threat.objects.filter(security_log=log).first()
            prediction = ModelPrediction.objects.filter(security_log=log).order_by("-created_at").first()
            events.append(
                {
                    "log_id": log.id,
                    "source": log.source,
                    "event_type": log.event_type,
                    "action": log.action,
                    "file_path": log.file_path,
                    "message": log.message,
                    "created_at": log.created_at.isoformat(),
                    "metadata": log.metadata,
                    "threat_id": threat.id if threat else None,
                    "threat_level": threat.threat_level if threat else None,
                    "confidence_score": threat.confidence_score if threat else (prediction.total_score if prediction else 0.0),
                    "ai_score": prediction.ai_score if prediction else None,
                }
            )
        return Response({"status": "ok", "events": events}, status=status.HTTP_200_OK)
