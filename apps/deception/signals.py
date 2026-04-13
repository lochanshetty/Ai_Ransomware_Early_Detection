from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.deception.services.honeypot_monitor import process_security_log
from apps.detection.models import SecurityLog


@receiver(post_save, sender=SecurityLog)
def detect_honeypot_access(sender, instance: SecurityLog, created: bool, **kwargs):
    """Runs deception monitor when new telemetry logs are created."""

    if not created:
        return

    process_security_log(instance)
