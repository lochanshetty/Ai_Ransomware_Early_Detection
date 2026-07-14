from pathlib import Path
from datetime import timedelta
import time

from django.conf import settings
from django.utils import timezone

from apps.detection.models import Alert, FeatureRecord, ModelPrediction, SecurityLog, Threat, ThreatLevel
from apps.detection.services.hybrid_scorer import score_event
from apps.detection.services.model_loader import model_loader
from apps.detection.services.response_engine import response_engine
from feature_extraction.aggregator import FeatureAggregator


_feature_aggregator = FeatureAggregator(
    window_seconds=getattr(settings, "CRDS_FEATURE_WINDOW_SECONDS", 20.0),
)


def _build_features(log: SecurityLog, *, honeypot_hit: bool = False) -> "FeatureVector":
    metadata = log.metadata or {}
    return _feature_aggregator.build(
        file_path=metadata.get("file_path") or log.file_path,
        action=log.action or metadata.get("event_action", ""),
        previous_path=metadata.get("previous_path", ""),
        pid=metadata.get("pid"),
        process_known=bool(metadata.get("process_known", True)),
        yara_match=bool(metadata.get("yara_match")),
        honeypot_hit=honeypot_hit,
        blacklist_hit=bool(metadata.get("blacklist_hit")),
    )


def _check_honeypot(log: SecurityLog) -> tuple[bool, object | None]:
    from apps.deception.models import HoneypotFile

    metadata = log.metadata or {}
    file_path = metadata.get("file_path") or log.file_path
    if not file_path:
        return False, None

    normalized_path = str(Path(file_path).resolve())
    honeypot = HoneypotFile.objects.filter(file_path=normalized_path).first()
    access_events = {"file_access", "file_open", "file_read", "file_modify", "file_write", "file_event"}
    access_actions = {"create", "modify", "rename", "delete"}
    if not honeypot or log.event_type not in access_events:
        return False, None
    if log.event_type == "file_event" and log.action not in access_actions:
        return False, None

    if not honeypot.is_triggered:
        honeypot.is_triggered = True
        honeypot.save(update_fields=["is_triggered"])

    return True, honeypot


def _persist_features(log: SecurityLog, features) -> FeatureRecord:
    return FeatureRecord.objects.create(
        security_log=log,
        feature_vector=features.to_dict(),
        feature_names=features.names,
    )


def _persist_prediction(log: SecurityLog, threat: Threat | None, hybrid_score, latency_ms: float) -> ModelPrediction:
    return ModelPrediction.objects.create(
        security_log=log,
        threat=threat,
        model_name=model_loader.model_info.get("name", "unknown"),
        model_version=model_loader.model_info.get("version", ""),
        ai_score=hybrid_score.ai_score,
        rule_score=hybrid_score.rule_score,
        total_score=hybrid_score.total_score,
        feature_importance=hybrid_score.feature_importance,
        prediction_latency_ms=latency_ms,
    )


def _create_alert_for_threat(threat: Threat):
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
    """Runs hybrid detection pipeline for one security log."""

    started = time.perf_counter()
    honeypot_hit, honeypot = _check_honeypot(log)
    features = _build_features(log, honeypot_hit=honeypot_hit)
    _persist_features(log, features)

    metadata = log.metadata or {}
    hybrid = score_event(
        log,
        features,
        honeypot_hit=honeypot_hit,
        yara_match=bool(metadata.get("yara_match")),
        blacklist_hit=bool(metadata.get("blacklist_hit")),
        whitelist_hit=bool(metadata.get("whitelist_hit")),
    )

    threshold = getattr(settings, "CRDS_THRESHOLD_MEDIUM", 0.5)
    is_suspicious = hybrid.total_score >= threshold or honeypot_hit

    threat = Threat.objects.filter(security_log=log).first()
    if is_suspicious and not threat:
        analysis_payload = {
            **hybrid.to_dict(),
            "process_name": features.process_features.get("process_name"),
            "executable_path": features.process_features.get("executable_path"),
            "pid": features.process_features.get("pid"),
            "file_hash_sha256": features.extras.get("file_hash_sha256"),
            "honeypot_triggered": honeypot_hit,
            "honeypot_path": honeypot.file_path if honeypot else None,
        }
        threat = Threat.objects.create(
            security_log=log,
            threat_level=hybrid.threat_level,
            threat_type=hybrid.threat_type,
            confidence_score=hybrid.total_score,
            message=hybrid.reason,
            reason=hybrid.explanation,
            analysis_payload=analysis_payload,
        )
        _create_alert_for_threat(threat)

        response_actions = response_engine.execute(
            confidence=hybrid.total_score,
            process_pid=features.process_features.get("pid"),
            file_path=features.extras.get("file_path", ""),
            threat_id=threat.id,
        )
        if response_actions:
            payload = threat.analysis_payload or {}
            payload["response_actions"] = [action.to_dict() for action in response_actions]
            threat.analysis_payload = payload
            threat.save(update_fields=["analysis_payload"])

    latency_ms = (time.perf_counter() - started) * 1000.0
    _persist_prediction(log, threat, hybrid, latency_ms)

    return {
        "log_id": log.id,
        "is_suspicious": is_suspicious,
        "threat_id": threat.id if threat else None,
        "confidence_score": hybrid.total_score,
        "threat_level": hybrid.threat_level,
        "threat_type": hybrid.threat_type,
        "reason": hybrid.explanation,
        "ai_score": hybrid.ai_score,
        "rule_score": hybrid.rule_score,
        "feature_importance": hybrid.feature_importance,
        "mitre_techniques": hybrid.mitre_techniques,
        "prediction_latency_ms": latency_ms,
    }


def detect_threat(log: SecurityLog) -> dict:
    """Public detection entrypoint used by signal-driven integrations."""

    return analyze_log(log)
