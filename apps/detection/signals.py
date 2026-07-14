from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.detection.models import SecurityLog
from apps.detection.services.pipeline import detect_threat


def _broadcast_detection_result(log: SecurityLog, result: dict) -> None:
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            "crds_events",
            {
                "type": "crds_event",
                "payload": {
                    "event": "detection_result",
                    "log_id": log.id,
                    "file_path": log.file_path,
                    "action": log.action,
                    **result,
                },
            },
        )
    except Exception:  # noqa: BLE001
        pass


@receiver(post_save, sender=SecurityLog)
def run_detection_pipeline(sender, instance: SecurityLog, created: bool, **kwargs):
    """Auto-runs detect_threat whenever a new SecurityLog record is created."""

    if created:
        result = detect_threat(instance)
        if result.get("is_suspicious"):
            print(
                f"[DETECTION] {result.get('threat_type')} | "
                f"level={result.get('threat_level')} | "
                f"score={result.get('confidence_score', 0):.2f} | log_id={instance.id}"
            )
        _broadcast_detection_result(instance, result)
