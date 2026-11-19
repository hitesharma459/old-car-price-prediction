"""Regression metrics used to compare models."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    """R2, MAE, MSE, RMSE in rupees, plus R2 / MAPE for context."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mse = mean_squared_error(y_true, y_pred)
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "mape_pct": float(np.mean(np.abs(y_true - y_pred) / y_true) * 100),
        "r2_log": float(r2_score(np.log1p(y_true), np.log1p(np.clip(y_pred, 0, None)))),
    }


def log_r2_scorer(estimator, X, y) -> float:
    """CV scorer: R2 on log-price, so cheap cars count as much as luxury ones."""
    pred = np.clip(estimator.predict(X), 0, None)
    return float(r2_score(np.log1p(y), np.log1p(pred)))
