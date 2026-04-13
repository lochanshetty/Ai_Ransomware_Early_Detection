from pathlib import Path

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.deception.models import HoneypotAccessEvent, HoneypotFile
from apps.detection.models import Alert, SecurityLog


@receiver(post_save, sender=SecurityLog)
def detect_honeypot_access(sender, instance: SecurityLog, created: bool, **kwargs):
    """Triggers immediate alerts when a honeypot file is accessed."""

    if not created:
        return

    metadata = instance.metadata or {}
    raw_file_path = metadata.get("file_path")
    if not raw_file_path:
        return

    normalized_path = str(Path(raw_file_path).resolve())
    honeypot_file = HoneypotFile.objects.filter(
        file_path=normalized_path,
        is_active=True,
    ).first()
    if not honeypot_file:
        return

    access_event, was_created = HoneypotAccessEvent.objects.get_or_create(
        honeypot_file=honeypot_file,
        security_log=instance,
        defaults={"process_name": str(metadata.get("process_name", ""))},
    )
    if not was_created:
        return

    Alert.objects.create(
        title="Honeypot file access detected",
        description=(
            f"Decoy file accessed: {honeypot_file.file_path}. "
            f"Process: {access_event.process_name or 'unknown'}."
        ),
        severity="high",
        status="open",
    )
