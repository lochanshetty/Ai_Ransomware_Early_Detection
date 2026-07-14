"""Model evaluation utilities."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

from training.datasets import generate_synthetic_dataset


def evaluate_saved_model(model_path: Path) -> dict:
    artifact = joblib.load(model_path)
    model = artifact["model"]
    scaler = artifact["scaler"]
    model_type = artifact["model_type"]

    X, y = generate_synthetic_dataset(samples=1000, seed=99)
    X_scaled = scaler.transform(X)

    if model_type == "isolation_forest":
        raw = model.predict(X_scaled)
        y_pred = np.where(raw == -1, 1, 0)
    else:
        y_pred = model.predict(X_scaled)

    return {
        "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
        "classification_report": classification_report(y, y_pred, output_dict=True),
    }
