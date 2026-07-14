from pathlib import Path

from apps.deception.models import HoneypotFile
from apps.detection.models import SecurityLog

ACCESS_EVENTS = {"file_access", "file_open", "file_read", "file_modify", "file_write", "file_event"}
ACCESS_ACTIONS = {"create", "modify", "rename", "delete"}


def process_security_log(log: SecurityLog) -> dict:
    """
    Marks honeypot files as triggered. Threat creation is owned by detection pipeline.
    """

    metadata = log.metadata or {}
    file_path = metadata.get("file_path") or log.file_path
    if not file_path:
        return {"triggered": False}

    normalized_path = str(Path(file_path).resolve())
    honeypot = HoneypotFile.objects.filter(file_path=normalized_path).first()
    if not honeypot:
        return {"triggered": False}

    if log.event_type not in ACCESS_EVENTS:
        return {"triggered": False}
    if log.event_type == "file_event" and log.action not in ACCESS_ACTIONS:
        return {"triggered": False}

    if not honeypot.is_triggered:
        honeypot.is_triggered = True
        honeypot.save(update_fields=["is_triggered"])
        print(f"[DECEPTION] Honeypot triggered! {honeypot.file_path}")

    return {"triggered": True, "honeypot_path": honeypot.file_path}
