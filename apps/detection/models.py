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
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.source}:{self.event_type}"


class DetectedThreat(TimeStampedModel):
    """Represents a threat candidate produced by the AI detection layer."""

    threat_name = models.CharField(max_length=255)
    confidence_score = models.FloatField()
    severity = models.CharField(max_length=32, default="medium")
    analysis_payload = models.JSONField(default=dict, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.threat_name} ({self.severity})"


class Alert(TimeStampedModel):
    """Stores actionable alerts consumed by API and dashboard layers."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, default="open")
    severity = models.CharField(max_length=32, default="medium")
    threat = models.ForeignKey(
        DetectedThreat,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alerts",
    )

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"
