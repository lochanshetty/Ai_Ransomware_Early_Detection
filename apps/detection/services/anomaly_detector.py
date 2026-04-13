from __future__ import annotations

from typing import Iterable

from sklearn.ensemble import IsolationForest

from apps.detection.models import SecurityLog


def _extract_feature_vector(log: SecurityLog) -> list[float]:
    """Converts a SecurityLog record into numeric features for inference."""

    metadata = log.metadata or {}
    file_mod_count = float(metadata.get("file_mod_count", 0))
    files_accessed_count = float(metadata.get("files_accessed_count", 0))
    process_unknown = 1.0 if metadata.get("process_known", True) is False else 0.0

    return [
        file_mod_count,
        files_accessed_count,
        process_unknown,
        float(len(log.message or "")),
    ]


def score_logs(logs: Iterable[SecurityLog]) -> dict[int, float]:
    """
    Scores security logs with Isolation Forest.

    Returns a map of log_id -> anomaly_score in [0, 1], where higher means
    more anomalous/suspicious.
    """

    logs = list(logs)
    if not logs:
        return {}

    features = [_extract_feature_vector(log) for log in logs]
    contamination = min(0.4, max(0.05, 1 / max(len(features), 1)))
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    model.fit(features)
    raw_scores = model.decision_function(features)

    # Convert to "higher is more anomalous" and normalize 0..1.
    anomaly = [-score for score in raw_scores]
    minimum = min(anomaly)
    maximum = max(anomaly)
    spread = (maximum - minimum) or 1.0

    normalized = [(score - minimum) / spread for score in anomaly]
    return {log.id: normalized[idx] for idx, log in enumerate(logs)}
