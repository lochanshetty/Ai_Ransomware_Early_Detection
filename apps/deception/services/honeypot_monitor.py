from pathlib import Path

from apps.deception.models import HoneypotFile
from apps.detection.models import SecurityLog, Threat, ThreatLevel

ACCESS_EVENTS = {"file_access", "file_open", "file_read", "file_modify", "file_write", "file_event"}
ACCESS_ACTIONS = {"create", "modify", "rename", "delete"}


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
    if not honeypot:
        return {"triggered": False, "threat_id": None}

    if log.event_type not in ACCESS_EVENTS:
        return {"triggered": False, "threat_id": None}

    if log.event_type == "file_event" and log.action not in ACCESS_ACTIONS:
        return {"triggered": False, "threat_id": None}

    if not honeypot.is_triggered:
        honeypot.is_triggered = True
        honeypot.save(update_fields=["is_triggered"])
        print(f"[DECEPTION] Honeypot triggered! {honeypot.file_path}")

    threat = Threat.objects.filter(
        security_log=log,
        threat_level=ThreatLevel.HIGH,
        threat_type="Critical Threat",
    ).first()
    if not threat:
        threat = Threat.objects.create(
            security_log=log,
            threat_level=ThreatLevel.HIGH,
            threat_type="Critical Threat",
            confidence_score=1.0,
            message="Honeypot file triggered",
            reason="Honeypot triggered!",
            analysis_payload={
                "honeypot_triggered": True,
                "honeypot_path": honeypot.file_path,
                "source": log.source,
                "event_type": log.event_type,
                "action": log.action,
                "source_ip": f"203.0.113.{(log.id or 1) % 200 + 1}",
                "process_name": metadata.get("process_name", "demo_simulation"),
                "file_origin": "demo_files",
                "behavior_pattern": "Honeypot access and tamper attempt",
                "encryption_type": "Fernet (AES-based) - Simulated",
                "intel_note": "Simulated Threat Intelligence",
            },
        )
        print(f"[DETECTION] Threat detected (honeypot): log_id={log.id}")

    return {"triggered": True, "threat_id": threat.id}
