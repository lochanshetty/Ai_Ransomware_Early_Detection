from django.contrib import admin

from apps.detection.models import Alert, SecurityLog, Threat


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ("source", "event_type", "created_at")
    search_fields = ("source", "event_type", "message")


@admin.register(Threat)
class ThreatAdmin(admin.ModelAdmin):
    list_display = ("security_log", "threat_level", "confidence_score", "detected_at")
    list_filter = ("threat_level",)
    search_fields = ("reason", "security_log__source", "security_log__message")


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "status", "created_at")
    list_filter = ("severity", "status")
    search_fields = ("title", "description")
