from django.shortcuts import render

from apps.detection.models import SecurityLog, Threat
from apps.monitoring.services import monitor_runtime


def dashboard_home(request):
    """Shows high-level system status and recent security activity."""

    status = monitor_runtime.status()
    recent_logs = SecurityLog.objects.order_by("-created_at")[:10]
    recent_threats = Threat.objects.select_related("security_log").order_by("-detected_at")[:10]

    context = {
        "monitor_status": status,
        "recent_logs": recent_logs,
        "recent_threats": recent_threats,
        "total_logs": SecurityLog.objects.count(),
        "total_threats": Threat.objects.count(),
    }
    return render(request, "dashboard/dashboard.html", context)


def logs_view(request):
    """Displays recent security logs in a structured table."""

    logs = SecurityLog.objects.order_by("-created_at")[:100]
    return render(request, "dashboard/logs.html", {"logs": logs})


def alerts_view(request):
    """Displays recently detected threats as dashboard alerts."""

    threats = Threat.objects.select_related("security_log").order_by("-detected_at")[:100]
    return render(request, "dashboard/alerts.html", {"threats": threats})
