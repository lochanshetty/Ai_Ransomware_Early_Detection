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

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["source", "action"]),
            models.Index(fields=["file_path"]),
        ]

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

    class Meta:
        indexes = [
            models.Index(fields=["-detected_at"]),
            models.Index(fields=["threat_level"]),
        ]

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

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"


class FeatureRecord(TimeStampedModel):
    """Persisted behavioral feature vectors for training and forensics."""

    security_log = models.ForeignKey(
        SecurityLog,
        on_delete=models.CASCADE,
        related_name="feature_records",
    )
    feature_vector = models.JSONField(default=dict)
    feature_names = models.JSONField(default=list)

    class Meta:
        indexes = [models.Index(fields=["-created_at"])]


class ModelPrediction(TimeStampedModel):
    """Stores ML inference results and latency metrics."""

    security_log = models.ForeignKey(
        SecurityLog,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    threat = models.ForeignKey(
        Threat,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="predictions",
    )
    model_name = models.CharField(max_length=128)
    model_version = models.CharField(max_length=64, blank=True)
    ai_score = models.FloatField(default=0.0)
    rule_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    feature_importance = models.JSONField(default=dict, blank=True)
    prediction_latency_ms = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["model_name"]),
        ]


class ProcessRecord(TimeStampedModel):
    """Process metadata captured during detection events."""

    security_log = models.ForeignKey(
        SecurityLog,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="process_records",
    )
    pid = models.IntegerField(default=0)
    process_name = models.CharField(max_length=255, blank=True)
    executable_path = models.CharField(max_length=1024, blank=True)
    username = models.CharField(max_length=255, blank=True)
    parent_pid = models.IntegerField(default=0)
    cmdline = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["pid"]),
            models.Index(fields=["process_name"]),
        ]


class HashRecord(TimeStampedModel):
    """Known file hashes for whitelist/blacklist matching."""

    sha256 = models.CharField(max_length=64, unique=True)
    label = models.CharField(
        max_length=32,
        choices=[("whitelist", "Whitelist"), ("blacklist", "Blacklist")],
    )
    source = models.CharField(max_length=128, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["label"])]


class AuditLog(TimeStampedModel):
    """API audit trail for security-sensitive operations."""

    user = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=128)
    path = models.CharField(max_length=512, blank=True)
    method = models.CharField(max_length=16, blank=True)
    status_code = models.IntegerField(default=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["action"]),
        ]
