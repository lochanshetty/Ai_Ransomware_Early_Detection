"""Load persisted ML models for inference."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads versioned joblib models from saved_models/ registry."""

    def __init__(self, base_dir: Path | None = None):
        try:
            from django.conf import settings as django_settings
            self.base_dir = base_dir or Path(django_settings.BASE_DIR)
        except Exception:  # noqa: BLE001
            self.base_dir = base_dir or Path(__file__).resolve().parents[3]
        self.registry_path = self.base_dir / "saved_models" / "model_registry.json"
        self._artifact: dict[str, Any] | None = None
        self._active_name: str | None = None

    def _load_registry(self) -> dict:
        if not self.registry_path.exists():
            return {"models": {}, "active_model": None}
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def reload(self, model_name: str | None = None) -> bool:
        registry = self._load_registry()
        active = model_name or registry.get("active_model")
        if not active:
            logger.warning("No active model in registry")
            return False

        model_info = registry.get("models", {}).get(active)
        if not model_info:
            logger.warning("Model %s not found in registry", active)
            return False

        path = self.base_dir / model_info["path"]
        if not path.exists():
            logger.warning("Model artifact missing: %s", path)
            return False

        self._artifact = joblib.load(path)
        self._active_name = active
        logger.info("Loaded model %s from %s", active, path)
        return True

    @property
    def is_ready(self) -> bool:
        return self._artifact is not None

    @property
    def model_info(self) -> dict:
        if not self._artifact:
            return {}
        return {
            "name": self._active_name,
            "type": self._artifact.get("model_type"),
            "version": self._artifact.get("version"),
            "trained_at": self._artifact.get("trained_at"),
            "metrics": self._artifact.get("metrics", {}),
        }

    def predict_proba(self, feature_vector: list[float]) -> tuple[float, dict]:
        """
        Returns (malware_probability, explanation_dict).
        Falls back to neutral score if model unavailable.
        """

        if not self._artifact and not self.reload():
            return 0.0, {"error": "model_not_loaded"}

        model = self._artifact["model"]
        scaler = self._artifact["scaler"]
        model_type = self._artifact["model_type"]
        feature_names = self._artifact.get("feature_names", [])

        X = np.array([feature_vector], dtype=np.float64)
        X_scaled = scaler.transform(X)

        if model_type == "isolation_forest":
            raw_score = -float(model.decision_function(X_scaled)[0])
            probability = float(1 / (1 + np.exp(-raw_score)))
        else:
            probability = float(model.predict_proba(X_scaled)[0][1])

        importance: dict[str, float] = {}
        if hasattr(model, "feature_importances_") and feature_names:
            pairs = sorted(
                zip(feature_names, model.feature_importances_, strict=False),
                key=lambda item: item[1],
                reverse=True,
            )
            importance = {name: float(value) for name, value in pairs[:10]}

        return probability, {
            "model_name": self._active_name,
            "model_type": model_type,
            "probability": probability,
            "top_features": importance,
        }


# Singleton used by detection pipeline
model_loader = ModelLoader()
