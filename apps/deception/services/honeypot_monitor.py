from pathlib import Path

from apps.deception.models import HoneypotFile
from apps.detection.models import SecurityLog

ACCESS_EVENTS = {"file_access", "file_open", "file_read", "file_modify", "file_write"}


def process_security_log(log: SecurityLog) -> dict:
    """
    Detects honeypot access/modification and marks honeypot as triggered.

    Threat creation is owned by detection.detect_threat to keep one authority.
    """

    metadata = log.metadata or {}
    file_path = metadata.get("file_path")
    if not file_path:
        return {"triggered": False, "threat_id": None}

    normalized_path = str(Path(file_path).resolve())
    honeypot = HoneypotFile.objects.filter(file_path=normalized_path).first()
    if not honeypot or log.event_type not in ACCESS_EVENTS:
        return {"triggered": False, "threat_id": None}

    if not honeypot.is_triggered:
        honeypot.is_triggered = True
        honeypot.save(update_fields=["is_triggered"])
    return {"triggered": True, "threat_id": None}
