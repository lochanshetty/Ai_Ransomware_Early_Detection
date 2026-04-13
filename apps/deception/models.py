from django.db import models


class HoneypotFile(models.Model):
    """Registry of decoy files used to detect unauthorized file access."""

    display_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=512, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file_path


class HoneypotAccessEvent(models.Model):
    """Tracks detected accesses against honeypot files."""

    honeypot_file = models.ForeignKey(
        HoneypotFile,
        on_delete=models.CASCADE,
        related_name="access_events",
    )
    security_log = models.ForeignKey(
        "detection.SecurityLog",
        on_delete=models.CASCADE,
        related_name="honeypot_hits",
    )
    process_name = models.CharField(max_length=255, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("honeypot_file", "security_log"),
                name="unique_honeypot_hit_per_log",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.honeypot_file_id}:{self.security_log_id}"
