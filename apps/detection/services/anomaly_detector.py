"""
Backward-compatible wrapper delegating to persisted model loader.
"""

from __future__ import annotations

from typing import Iterable

from apps.detection.models import SecurityLog
from apps.detection.services.model_loader import model_loader
from feature_extraction.aggregator import FeatureAggregator

_aggregator = FeatureAggregator()


def _extract_feature_vector(log: SecurityLog) -> list[float]:
    metadata = log.metadata or {}
    features = _aggregator.build(
        file_path=metadata.get("file_path") or log.file_path,
        action=log.action or metadata.get("event_action", ""),
        previous_path=metadata.get("previous_path", ""),
        pid=metadata.get("pid"),
        process_known=bool(metadata.get("process_known", True)),
        yara_match=bool(metadata.get("yara_match")),
        honeypot_hit=bool(metadata.get("honeypot_hit")),
        blacklist_hit=bool(metadata.get("blacklist_hit")),
    )
    return features.as_array()


def score_logs(logs: Iterable[SecurityLog]) -> dict[int, float]:
    """Scores logs using the persisted ML model."""

    if not model_loader.is_ready:
        model_loader.reload()

    results: dict[int, float] = {}
    for log in logs:
        vector = _extract_feature_vector(log)
        probability, _meta = model_loader.predict_proba(vector)
        results[log.id] = probability
    return results
