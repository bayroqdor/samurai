"""
Uzbek spam classifier (char n-gram TF-IDF + logistic regression).

Trained by ``python -m uzspam_model.train``; a few MB in RAM and well under a
millisecond per message, so it stays loaded and is not managed by ml_manager.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MODEL_PATH = Path("uzspam_model/model.joblib")

_artifact: dict[str, Any] | None = None
_load_failed = False
_lock = threading.Lock()


def _load() -> dict[str, Any] | None:
    global _artifact, _load_failed
    with _lock:
        if _artifact is None and not _load_failed:
            try:
                import joblib  # optional dependency, only needed when the model is used

                # joblib unpickles: only ever load the artifact produced by our own
                # training script from the repository, never a downloaded file
                _artifact = joblib.load(MODEL_PATH)
                logger.info(
                    "Loaded Uzbek spam model (trained %s, threshold %.3f)",
                    _artifact.get("trained_at"), _artifact.get("threshold", 0.5),
                )
            except Exception:
                _load_failed = True
                logger.exception("Uzbek spam model unavailable at %s", MODEL_PATH)
        return _artifact


def spam_probability(text: str) -> float | None:
    """Probability that ``text`` is spam, or None if the model is unavailable."""
    artifact = _load()
    if artifact is None:
        return None
    return float(artifact["pipeline"].predict_proba([text])[0, 1])


def default_threshold() -> float:
    artifact = _load()
    return float(artifact.get("threshold", 0.5)) if artifact else 0.5


def is_loaded() -> bool:
    return _artifact is not None
