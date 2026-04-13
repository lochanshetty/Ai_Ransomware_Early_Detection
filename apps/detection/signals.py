from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.detection.models import SecurityLog
from apps.detection.services.pipeline import detect_threat


@receiver(post_save, sender=SecurityLog)
def run_detection_pipeline(sender, instance: SecurityLog, created: bool, **kwargs):
    """Auto-runs detect_threat whenever a new SecurityLog record is created."""

    if created:
        detect_threat(instance)
