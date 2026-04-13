from django.urls import path

from apps.api.views import AlertListCreateAPIView
from apps.detection.views import DetectAnalyzeAPIView, ThreatListAPIView
from apps.monitoring.views import MonitorStartAPIView, MonitorStatusAPIView

urlpatterns = [
    # Monitoring control endpoints.
    path("monitor/start", MonitorStartAPIView.as_view(), name="monitor-start"),
    path("monitor/status", MonitorStatusAPIView.as_view(), name="monitor-status"),
    # AI detection endpoint.
    path("detect/analyze", DetectAnalyzeAPIView.as_view(), name="detect-analyze"),
    path("detect/threats", ThreatListAPIView.as_view(), name="detect-threats"),
    # Alert management endpoint.
    path("alerts/", AlertListCreateAPIView.as_view(), name="alerts-list-create"),
]
