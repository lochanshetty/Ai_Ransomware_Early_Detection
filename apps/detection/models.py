from django.db import models


class TimeStampedModel(models.Model):
    """Reusable audit fields for all persisted security records."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SecurityLog(TimeStampedModel):
    """Stores normalized runtime telemetry emitted by monitoring modules."""

    source = models.CharField(max_length=128)
    event_type = models.CharField(max_length=128)
    action = models.CharField(max_length=64, blank=True)
    file_path = models.CharField(max_length=512, blank=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.source}:{self.event_type}"


class ThreatLevel(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class Threat(TimeStampedModel):
    """Represents a suspicious event produced by the detection module."""

    security_log = models.ForeignKey(
        SecurityLog,
        on_delete=models.CASCADE,
        related_name="threats",
    )
    threat_level = models.CharField(
        max_length=16,
        choices=ThreatLevel.choices,
        default=ThreatLevel.MEDIUM,
    )
    threat_type = models.CharField(max_length=64, default="Normal")
    confidence_score = models.FloatField()
    detected_at = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    analysis_payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.security_log_id}::{self.threat_level}"


class Alert(TimeStampedModel):
    """Stores actionable alerts consumed by API and dashboard layers."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, default="open")
    severity = models.CharField(max_length=32, default="medium")
    threat = models.ForeignKey(
        Threat,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alerts",
    )

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"
