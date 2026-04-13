from apps.detection.models import SecurityLog, Threat, ThreatLevel
from apps.detection.services.anomaly_detector import score_logs
from apps.detection.services.rule_engine import heuristic_assessment


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
