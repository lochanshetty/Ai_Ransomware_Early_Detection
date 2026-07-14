"""Synthetic and log-derived datasets for CRDS model training."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from feature_extraction.aggregator import FEATURE_NAMES


def generate_synthetic_dataset(samples: int = 2000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate labeled synthetic behavioral feature data.

    Label 1 = ransomware-like, 0 = benign.
    """

    rng = np.random.default_rng(seed)
    feature_count = len(FEATURE_NAMES)
    X = np.zeros((samples, feature_count), dtype=np.float64)
    y = np.zeros(samples, dtype=np.int32)

    benign_count = samples // 2
    for idx in range(samples):
        if idx < benign_count:
            X[idx] = rng.uniform(0, 0.3, size=feature_count)
            X[idx, FEATURE_NAMES.index("process_reputation")] = rng.uniform(0.6, 0.95)
            y[idx] = 0
        else:
            X[idx] = rng.uniform(0.2, 1.0, size=feature_count)
            X[idx, FEATURE_NAMES.index("files_modified_per_second")] = rng.uniform(2.0, 15.0)
            X[idx, FEATURE_NAMES.index("rename_ratio")] = rng.uniform(0.4, 1.0)
            X[idx, FEATURE_NAMES.index("entropy_delta")] = rng.uniform(2.0, 6.0)
            X[idx, FEATURE_NAMES.index("extension_changed")] = 1.0
            X[idx, FEATURE_NAMES.index("process_reputation")] = rng.uniform(0.1, 0.4)
            y[idx] = 1

    return X, y


def export_dataset(path: Path, X: np.ndarray, y: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "feature_names": FEATURE_NAMES,
        "X": X.tolist(),
        "y": y.tolist(),
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def load_dataset(path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        np.array(payload["X"], dtype=np.float64),
        np.array(payload["y"], dtype=np.int32),
        payload.get("feature_names", FEATURE_NAMES),
    )
