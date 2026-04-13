from django.contrib import admin

from apps.detection.models import Alert, DetectedThreat, SecurityLog


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ("source", "event_type", "created_at")
    search_fields = ("source", "event_type", "message")


@admin.register(DetectedThreat)
class DetectedThreatAdmin(admin.ModelAdmin):
    list_display = ("threat_name", "confidence_score", "severity", "is_confirmed")
    list_filter = ("severity", "is_confirmed")
    search_fields = ("threat_name",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "status", "created_at")
    list_filter = ("severity", "status")
    search_fields = ("title", "description")
