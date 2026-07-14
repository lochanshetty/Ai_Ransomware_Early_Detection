"""Offline model training for CRDS detection pipeline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from feature_extraction.aggregator import FEATURE_NAMES
from training.datasets import export_dataset, generate_synthetic_dataset, load_dataset

ROOT = Path(__file__).resolve().parents[1]
SAVED_MODELS = ROOT / "saved_models"
REGISTRY_PATH = SAVED_MODELS / "model_registry.json"


def _build_model(model_type: str):
    if model_type == "isolation_forest":
        return IsolationForest(n_estimators=200, contamination=0.15, random_state=42)
    if model_type == "random_forest":
        return RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    if model_type == "xgboost":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise RuntimeError("xgboost is not installed") from exc
        return XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            eval_metric="logloss",
        )
    if model_type == "lightgbm":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise RuntimeError("lightgbm is not installed") from exc
        return LGBMClassifier(n_estimators=200, random_state=42)
    raise ValueError(f"Unsupported model type: {model_type}")


def _evaluate(model_type: str, model, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    if model_type == "isolation_forest":
        raw = model.predict(X_test)
        y_pred = np.where(raw == -1, 1, 0)
        y_score = -model.decision_function(X_test)
    else:
        y_pred = model.predict(X_test)
        y_score = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }
    try:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_score))
    except ValueError:
        metrics["roc_auc"] = 0.0
    return metrics


def train_model(
    model_type: str = "random_forest",
    dataset_path: Path | None = None,
    output_name: str | None = None,
) -> dict:
    if dataset_path and dataset_path.exists():
        X, y, feature_names = load_dataset(dataset_path)
    else:
        X, y = generate_synthetic_dataset()
        feature_names = FEATURE_NAMES
        export_dataset(ROOT / "dataset" / "synthetic_ransomware.json", X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = _build_model(model_type)
    if model_type == "isolation_forest":
        model.fit(X_train_scaled)
    else:
        model.fit(X_train_scaled, y_train)

    metrics = _evaluate(model_type, model, X_test_scaled, y_test)

    version_name = output_name or f"{model_type}_v1"
    artifact = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "model_type": model_type,
        "version": version_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }

    SAVED_MODELS.mkdir(parents=True, exist_ok=True)
    artifact_path = SAVED_MODELS / f"{version_name}.joblib"
    joblib.dump(artifact, artifact_path)

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else {"models": {}}
    registry["active_model"] = version_name
    registry["feature_names"] = feature_names
    registry["models"][version_name] = {
        "path": str(artifact_path.relative_to(ROOT)).replace("\\", "/"),
        "type": model_type,
        "version": version_name,
        "trained_at": artifact["trained_at"],
        "metrics": metrics,
    }
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return {
        "model": version_name,
        "path": str(artifact_path),
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser(description="Train CRDS ransomware detection models")
    parser.add_argument(
        "--model",
        choices=["isolation_forest", "random_forest", "xgboost", "lightgbm"],
        default="random_forest",
    )
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()
    result = train_model(args.model, args.dataset, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
