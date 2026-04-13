from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.detection.models import SecurityLog
from apps.detection.services.pipeline import analyze_log


@receiver(post_save, sender=SecurityLog)
def run_detection_pipeline(sender, instance: SecurityLog, created: bool, **kwargs):
    """Auto-runs detection whenever a new SecurityLog record is created."""

    if created:
        analyze_log(instance)
