"""Hybrid threat scoring: AI + rules + honeypots + intel + lists."""

from __future__ import annotations

from dataclasses import dataclass, asdict

from django.conf import settings

from apps.detection.models import SecurityLog, ThreatLevel
from apps.detection.services.model_loader import model_loader
from apps.detection.services.rule_engine import heuristic_assessment
from feature_extraction.aggregator import FeatureVector


@dataclass
class HybridScore:
    total_score: float
    ai_score: float
    rule_score: float
    honeypot_score: float
    yara_score: float
    intel_score: float
    whitelist_adjustment: float
    threat_level: str
    threat_type: str
    reason: str
    mitre_techniques: list[str]
    feature_importance: dict
    rule_matches: list[str]
    explanation: str

    def to_dict(self) -> dict:
        return asdict(self)


def _level_from_score(score: float) -> ThreatLevel:
    high = getattr(settings, "CRDS_THRESHOLD_HIGH", 0.75)
    medium = getattr(settings, "CRDS_THRESHOLD_MEDIUM", 0.5)
    if score >= high:
        return ThreatLevel.HIGH
    if score >= medium:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW


def _rule_score_from_assessment(suspicious: bool, level: ThreatLevel) -> float:
    if not suspicious:
        return 0.0
    if level == ThreatLevel.HIGH:
        return 0.85
    if level == ThreatLevel.MEDIUM:
        return 0.55
    return 0.25


def _behavioral_burst_score(log: SecurityLog, features: FeatureVector) -> tuple[float, list[str], list[str]]:
    """Rule-based ransomware burst detection using extracted features."""

    file_feats = features.file_features
    matches: list[str] = []
    mitre: list[str] = []
    score = 0.0

    mod_rate = float(file_feats.get("files_modified_per_second", 0))
    rename_ratio = float(file_feats.get("rename_ratio", 0))
    entropy_delta = float(file_feats.get("entropy_delta", 0))
    extension_changed = float(file_feats.get("extension_changed", 0))

    if mod_rate >= 2.0:
        score += 0.25
        matches.append(f"High modification rate ({mod_rate:.1f}/s)")
        mitre.append("T1486")
    if rename_ratio >= 0.4:
        score += 0.25
        matches.append(f"High rename ratio ({rename_ratio:.2f})")
        mitre.append("T1486")
    if entropy_delta >= 2.0:
        score += 0.2
        matches.append(f"Entropy spike (+{entropy_delta:.2f})")
        mitre.append("T1027")
    if extension_changed >= 1.0:
        score += 0.2
        matches.append("Suspicious extension change")
        mitre.append("T1486")

    metadata = log.metadata or {}
    if metadata.get("has_ransom_note"):
        score += 0.15
        matches.append("Ransom note detected")
        mitre.append("T1491")

    return min(score, 1.0), matches, mitre


def score_event(
    log: SecurityLog,
    features: FeatureVector,
    *,
    honeypot_hit: bool = False,
    yara_match: bool = False,
    blacklist_hit: bool = False,
    whitelist_hit: bool = False,
) -> HybridScore:
    """Compute weighted hybrid threat score."""

    weights = getattr(settings, "CRDS_SCORE_WEIGHTS", {
        "ai": 0.35,
        "rules": 0.30,
        "honeypot": 0.20,
        "yara": 0.10,
        "intel": 0.05,
    })

    ai_score, ai_meta = model_loader.predict_proba(features.as_array())
    rule_suspicious, rule_level, rule_reason = heuristic_assessment(log)
    heuristic_score = _rule_score_from_assessment(rule_suspicious, rule_level)
    burst_score, rule_matches, mitre = _behavioral_burst_score(log, features)
    rule_score = max(heuristic_score, burst_score)

    honeypot_score = 1.0 if honeypot_hit else 0.0
    yara_score = 1.0 if yara_match else 0.0
    intel_score = 0.3 if blacklist_hit else 0.0
    whitelist_adjustment = -0.5 if whitelist_hit else 0.0

    total = (
        weights["ai"] * ai_score
        + weights["rules"] * rule_score
        + weights["honeypot"] * honeypot_score
        + weights["yara"] * yara_score
        + weights["intel"] * intel_score
        + whitelist_adjustment
    )
    if rule_suspicious and rule_level == ThreatLevel.HIGH:
        total = max(total, getattr(settings, "CRDS_THRESHOLD_MEDIUM", 0.5) + 0.05)
    total = max(0.0, min(total, 1.0))

    level = _level_from_score(total)
    if honeypot_hit:
        threat_type = "Critical Threat"
        reason = "Honeypot file accessed"
    elif total >= getattr(settings, "CRDS_THRESHOLD_HIGH", 0.75):
        threat_type = "Ransomware Behavior"
        reason = rule_reason if rule_matches else "AI + behavioral indicators"
    elif total >= getattr(settings, "CRDS_THRESHOLD_MEDIUM", 0.5):
        threat_type = "Suspicious Activity"
        reason = rule_reason or "Elevated behavioral score"
    else:
        threat_type = "Normal activity"
        reason = "Below detection threshold"

    explanation_parts = [
        f"AI probability: {ai_score:.2%}",
        f"Rule score: {rule_score:.2%}",
    ]
    if rule_matches:
        explanation_parts.append("Rules: " + "; ".join(rule_matches))
    if honeypot_hit:
        explanation_parts.append("Honeypot triggered")

    return HybridScore(
        total_score=total,
        ai_score=ai_score,
        rule_score=rule_score,
        honeypot_score=honeypot_score,
        yara_score=yara_score,
        intel_score=intel_score,
        whitelist_adjustment=whitelist_adjustment,
        threat_level=level.value if hasattr(level, "value") else str(level),
        threat_type=threat_type,
        reason=reason,
        mitre_techniques=sorted(set(mitre)),
        feature_importance=ai_meta.get("top_features", {}),
        rule_matches=rule_matches,
        explanation=" | ".join(explanation_parts),
    )
