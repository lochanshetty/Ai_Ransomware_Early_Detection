from pathlib import Path

from apps.detection.models import SecurityLog, Threat, ThreatLevel
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
        confidence_score=1.0,
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


def analyze_log(log: SecurityLog) -> dict:
    """Runs the combined detection pipeline for one security log."""

    scores = score_logs([log])
    anomaly_score = scores.get(log.id, 0.0)
    rule_suspicious, heuristic_level, reason = heuristic_assessment(log)
    model_suspicious = anomaly_score >= 0.7
    is_suspicious = rule_suspicious or model_suspicious
    final_level = _resolve_threat_level(anomaly_score, heuristic_level)

    threat = None
    if is_suspicious:
        threat = Threat.objects.create(
            security_log=log,
            threat_level=final_level,
            confidence_score=anomaly_score,
            reason=reason,
            analysis_payload={
                "rule_suspicious": rule_suspicious,
                "model_suspicious": model_suspicious,
                "anomaly_score": anomaly_score,
            },
        )

    return {
        "log_id": log.id,
        "is_suspicious": is_suspicious,
        "threat_id": threat.id if threat else None,
        "anomaly_score": anomaly_score,
        "threat_level": final_level,
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
