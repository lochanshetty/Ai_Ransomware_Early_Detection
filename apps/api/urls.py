from django.urls import path

from apps.api.views import (
    AlertListCreateAPIView,
    HealthCheckAPIView,
    SystemRunAttackAPIView,
    SystemStartMonitoringAPIView,
    SystemStatusAPIView,
    SystemStopAttackAPIView,
    SystemStopMonitoringAPIView,
)
from apps.deception.views import (
    HoneypotAccessReportAPIView,
    HoneypotCreateAPIView,
    HoneypotRefreshAPIView,
    HoneypotStatusAPIView,
    HoneypotTriggeredAPIView,
)
from apps.detection.views import DetectAnalyzeAPIView, ThreatListAPIView
from apps.monitoring.views import (
    DemoRunAPIView,
    MonitorLogsAPIView,
    MonitorStartAPIView,
    MonitorStatusAPIView,
    RegistryAddAPIView,
    RegistryListAPIView,
)

urlpatterns = [
    # Monitoring control endpoints.
    path("monitor/start", MonitorStartAPIView.as_view(), name="monitor-start"),
    path("monitor/status", MonitorStatusAPIView.as_view(), name="monitor-status"),
    path("monitor/logs", MonitorLogsAPIView.as_view(), name="monitor-logs"),
    path("demo/run", DemoRunAPIView.as_view(), name="demo-run"),
    path("registry/add", RegistryAddAPIView.as_view(), name="registry-add"),
    path("registry/list", RegistryListAPIView.as_view(), name="registry-list"),
    # AI detection endpoint.
    path("detect/analyze", DetectAnalyzeAPIView.as_view(), name="detect-analyze"),
    path("detect/threats", ThreatListAPIView.as_view(), name="detect-threats"),
    # Deception honeypot endpoints.
    path("honeypot/generate", HoneypotCreateAPIView.as_view(), name="honeypot-generate"),
    path("honeypot/create", HoneypotCreateAPIView.as_view(), name="honeypot-create"),
    path("honeypot/status", HoneypotStatusAPIView.as_view(), name="honeypot-status"),
    path("honeypot/triggered", HoneypotTriggeredAPIView.as_view(), name="honeypot-triggered"),
    path("honeypot/refresh", HoneypotRefreshAPIView.as_view(), name="honeypot-refresh"),
    path("deception/access", HoneypotAccessReportAPIView.as_view(), name="deception-access"),
    # Unified dashboard system controls.
    path("system/status", SystemStatusAPIView.as_view(), name="system-status"),
    path("system/start-monitoring", SystemStartMonitoringAPIView.as_view(), name="system-start-monitoring"),
    path("system/stop-monitoring", SystemStopMonitoringAPIView.as_view(), name="system-stop-monitoring"),
    path("system/run-attack", SystemRunAttackAPIView.as_view(), name="system-run-attack"),
    path("system/stop-attack", SystemStopAttackAPIView.as_view(), name="system-stop-attack"),
    # Alert management endpoint.
    path("alerts/", AlertListCreateAPIView.as_view(), name="alerts-list-create"),
    path("healthz", HealthCheckAPIView.as_view(), name="health-check"),
]
