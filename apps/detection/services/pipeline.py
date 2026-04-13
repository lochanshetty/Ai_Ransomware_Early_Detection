from pathlib import Path
from datetime import timedelta

from django.utils import timezone

from apps.detection.models import Alert, SecurityLog, Threat, ThreatLevel
from apps.detection.services.anomaly_detector import score_logs
from apps.detection.services.rule_engine import heuristic_assessment


def _handle_honeypot_access(log: SecurityLog) -> dict | None:
    """
    Handles honeypot hits with immediate HIGH threat and bypasses AI flow.
    """

    from apps.deception.models import HoneypotFile

    metadata = log.metadata or {}
    file_path = metadata.get("file_path")
    if not file_path:
        return None

    normalized_path = str(Path(file_path).resolve())
    honeypot = HoneypotFile.objects.filter(file_path=normalized_path).first()
    access_events = {"file_access", "file_open", "file_read", "file_modify", "file_write"}
    if not honeypot or log.event_type not in access_events:
        return None

    if not honeypot.is_triggered:
        honeypot.is_triggered = True
        honeypot.save(update_fields=["is_triggered"])

    existing = Threat.objects.filter(
        security_log=log,
        threat_level=ThreatLevel.HIGH,
        reason="Honeypot file accessed",
    ).first()
    threat = existing or Threat.objects.create(
        security_log=log,
        threat_level=ThreatLevel.HIGH,
        threat_type="Honeypot Trigger",
        confidence_score=1.0,
        message="Honeypot file access detected",
        reason="Honeypot file accessed",
        analysis_payload={
            "bypassed_ai_detection": True,
            "honeypot_triggered": True,
            "honeypot_path": honeypot.file_path,
            "process_name": metadata.get("process_name"),
        },
    )

    return {
        "log_id": log.id,
        "is_suspicious": True,
        "threat_id": threat.id,
        "anomaly_score": 1.0,
        "threat_level": ThreatLevel.HIGH,
        "reason": "Honeypot file accessed",
    }


def _resolve_threat_level(anomaly_score: float, heuristic_level: ThreatLevel) -> ThreatLevel:
    if heuristic_level == ThreatLevel.HIGH or anomaly_score >= 0.8:
        return ThreatLevel.HIGH
    if heuristic_level == ThreatLevel.MEDIUM or anomaly_score >= 0.6:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW


def _classify_ransomware_activity(log: SecurityLog) -> tuple[bool, str, ThreatLevel, float, str, dict]:
    """Classifies monitored activity as GenieLocker-like, Generic, or Normal."""

    metadata = log.metadata or {}
    burst_modifications = int(metadata.get("file_mod_count", 0))
    if log.action == "rename" and burst_modifications >= 5:
        same_window_has_note = SecurityLog.objects.filter(
            source="monitoring",
            created_at__gte=timezone.now() - timedelta(seconds=20),
            action="create",
            file_path__iendswith="README.txt",
        ).exists()
        if same_window_has_note:
            return True, "Generic ransomware", ThreatLevel.HIGH, 0.98, "Rapid rename pattern with ransom note creation", {
                "file_mod_count": burst_modifications,
                "has_ransom_note": True,
            }
        return True, "GenieLocker-like ransomware", ThreatLevel.HIGH, 0.94, "Rapid rename pattern without ransom note", {
            "file_mod_count": burst_modifications,
            "has_ransom_note": False,
        }

    window_start = timezone.now() - timedelta(seconds=20)
    recent_logs = SecurityLog.objects.filter(
        source="monitoring",
        created_at__gte=window_start,
    )
    rename_count = recent_logs.filter(action="rename").count()
    has_ransom_note = recent_logs.filter(
        action="create",
        file_path__iendswith="README.txt",
    ).exists()

    context = {
        "rename_count_20s": rename_count,
        "has_ransom_note": has_ransom_note,
    }
    if rename_count >= 5 and not has_ransom_note:
        return True, "GenieLocker-like ransomware", ThreatLevel.HIGH, 0.94, "Rapid rename pattern without ransom note", context
    if rename_count >= 5 and has_ransom_note:
        return True, "Generic ransomware", ThreatLevel.HIGH, 0.98, "Rapid rename pattern with ransom note creation", context
    return False, "Normal activity", ThreatLevel.LOW, 0.1, "Normal activity", context


def _create_alert_for_threat(threat: Threat):
    """Creates an operator alert for suspicious threats."""

    if threat.threat_level == ThreatLevel.LOW:
        return
    Alert.objects.create(
        title=f"{threat.threat_type} detected",
        description=threat.message or threat.reason,
        severity=threat.threat_level.lower(),
        status="open",
        threat=threat,
    )


def analyze_log(log: SecurityLog) -> dict:
    """Runs the combined detection pipeline for one security log."""

    classified, threat_type, classified_level, classified_confidence, classified_msg, classified_ctx = _classify_ransomware_activity(log)
    if classified:
        threat = Threat.objects.filter(security_log=log).first()
        if not threat:
            threat = Threat.objects.create(
                security_log=log,
                threat_level=classified_level,
                threat_type=threat_type,
                confidence_score=classified_confidence,
                message=classified_msg,
                reason=classified_msg,
                analysis_payload=classified_ctx,
            )
            _create_alert_for_threat(threat)
        return {
            "log_id": log.id,
            "is_suspicious": True,
            "threat_id": threat.id,
            "anomaly_score": classified_confidence,
            "threat_level": classified_level,
            "threat_type": threat_type,
            "reason": classified_msg,
        }

    scores = score_logs([log])
    anomaly_score = float(scores.get(log.id, 0.0))
    rule_suspicious, heuristic_level, reason = heuristic_assessment(log)
    model_suspicious = bool(anomaly_score >= 0.7)
    is_suspicious = bool(rule_suspicious or model_suspicious)
    final_level = _resolve_threat_level(anomaly_score, heuristic_level)

    threat = None
    resolved_type = "Generic ransomware" if is_suspicious else "Normal activity"
    if is_suspicious:
        threat = Threat.objects.create(
            security_log=log,
            threat_level=final_level,
            threat_type=resolved_type,
            confidence_score=anomaly_score,
            message=reason,
            reason=reason,
            analysis_payload={
                "rule_suspicious": rule_suspicious,
                "model_suspicious": model_suspicious,
                "anomaly_score": float(anomaly_score),
            },
        )
        _create_alert_for_threat(threat)

    return {
        "log_id": log.id,
        "is_suspicious": is_suspicious,
        "threat_id": threat.id if threat else None,
        "anomaly_score": anomaly_score,
        "threat_level": final_level,
        "threat_type": resolved_type,
        "reason": reason,
    }


def detect_threat(log: SecurityLog) -> dict:
    """
    Public detection entrypoint used by signal-driven integrations.

    Runs detection and stores suspicious results in Threat model.
    """

    honeypot_result = _handle_honeypot_access(log)
    if honeypot_result:
        return honeypot_result

    return analyze_log(log)
