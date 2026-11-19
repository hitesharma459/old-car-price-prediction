"""Inference wrapper around the serialized scikit-learn pipeline."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .config import METADATA_PATH, MODEL_PATH, RAW_FEATURES

# (upper bound in INR, label) - used for the "estimated price category".
PRICE_CATEGORIES = [(300_000, "Budget"), (600_000, "Economy"), (1_200_000, "Mid-range"),
                    (3_000_000, "Premium"), (float("inf"), "Luxury")]


def price_category(price: float) -> str:
    return next(label for bound, label in PRICE_CATEGORIES if price < bound)


class PricePredictor:
    """Loads the trained pipeline once and serves predictions."""

    def __init__(self, model_path: Path = MODEL_PATH, metadata_path: Path = METADATA_PATH):
        if not Path(model_path).exists() or not Path(metadata_path).exists():
            raise FileNotFoundError(
                "Model artifacts not found. Train the model first: `python -m ml.train`")
        self.pipeline = joblib.load(model_path)
        self.metadata: dict[str, Any] = json.loads(Path(metadata_path).read_text())
        band = self.metadata["error_band_log"]
        self._low, self._high = band["low_q10"], band["high_q90"]

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        """Predict one car. ``features`` must contain every column in RAW_FEATURES."""
        missing = [c for c in RAW_FEATURES if c not in features]
        if missing:
            raise ValueError(f"Missing features: {', '.join(missing)}")
        frame = pd.DataFrame([{c: features[c] for c in RAW_FEATURES}])
        price = float(max(self.pipeline.predict(frame)[0], 0.0))
        # Range = typical (80%) error band measured on the held-out test set.
        low = float(np.expm1(np.log1p(price) + self._low))
        high = float(np.expm1(np.log1p(price) + self._high))
        return {"predicted_price": round(price), "price_low": round(low),
                "price_high": round(high), "price_category": price_category(price)}
