"""End-to-end training script.

    python -m ml.train

Steps: load -> clean -> EDA -> split -> compare models (CV) -> tune -> pick best
-> evaluate on the untouched test set -> save pipeline + metadata with Joblib.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from .config import (ARTIFACT_DIR, CLEAN_DATA_PATH, METADATA_PATH, MODEL_PATH, RANDOM_STATE,
                     RAW_DATA_PATH, RAW_FEATURES, TARGET, TEST_SIZE)
from .eda import run_eda
from .evaluate import log_r2_scorer, regression_metrics
from .preprocess import FeatureBuilder, clean_dataset

OWNER_LABELS = {0: "Unregistered / 0th owner", 1: "1st owner", 2: "2nd owner",
                3: "3rd owner", 4: "4th owner", 5: "5th owner"}


def build_pipeline(regressor) -> Pipeline:
    """FeatureBuilder -> encode/scale -> regressor, trained on log(price)."""
    encode = ColumnTransformer(
        [
            ("num", StandardScaler(), FeatureBuilder.NUMERIC),
            # rare categories (<3 rows) are pooled; unseen values never crash inference
            ("cat", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=3,
                                  sparse_output=False), FeatureBuilder.CATEGORICAL),
        ]
    )
    model = TransformedTargetRegressor(regressor=regressor, func=np.log1p, inverse_func=np.expm1)
    return Pipeline([("features", FeatureBuilder()), ("encode", encode), ("model", model)])


def candidates() -> dict:
    """Model name -> (regressor, hyper-parameter search space or None)."""
    rs = RANDOM_STATE
    return {
        "Linear Regression": (LinearRegression(), None),
        "Decision Tree": (DecisionTreeRegressor(random_state=rs), {
            "model__regressor__max_depth": [8, 12, 16, 24, None],
            "model__regressor__min_samples_leaf": [1, 2, 3, 5, 10]}),
        "Random Forest": (RandomForestRegressor(random_state=rs, n_jobs=-1), {
            "model__regressor__n_estimators": [150, 250],
            "model__regressor__max_depth": [None, 20, 30],
            "model__regressor__min_samples_leaf": [1, 2, 3],
            "model__regressor__max_features": [0.4, 0.6, 1.0]}),
        "Extra Trees": (ExtraTreesRegressor(random_state=rs, n_jobs=-1), {
            "model__regressor__n_estimators": [150, 250],
            "model__regressor__max_depth": [None, 20, 30],
            "model__regressor__min_samples_leaf": [1, 2, 3],
            "model__regressor__max_features": [0.4, 0.6, 1.0]}),
        "Gradient Boosting": (GradientBoostingRegressor(random_state=rs), {
            "model__regressor__n_estimators": [200, 300],
            "model__regressor__learning_rate": [0.05, 0.1],
            "model__regressor__max_depth": [3, 4, 5],
            "model__regressor__subsample": [0.7, 0.85, 1.0],
            "model__regressor__min_samples_leaf": [1, 3, 5]}),
    }


def build_catalog(df: pd.DataFrame) -> dict:
    """Form options derived from the real data (no invented values)."""
    brands = {}
    for brand, g in df.groupby("brand"):
        models = []
        for model, m in g.groupby("model"):
            models.append({
                "name": model, "count": int(len(m)),
                "median_engine_cc": int(m["engine_cc"].median()),
                "typical_seats": int(m["seats"].mode().iloc[0]),
                "fuel_types": sorted(m["fuel_type"].unique().tolist()),
                "transmissions": sorted(m["transmission"].unique().tolist()),
            })
        brands[brand] = sorted(models, key=lambda x: -x["count"])
    return {
        "brands": dict(sorted(brands.items())),
        "fuel_types": sorted(df["fuel_type"].unique().tolist()),
        "transmissions": sorted(df["transmission"].unique().tolist()),
        "ownership": [{"value": int(v), "label": OWNER_LABELS.get(int(v), f"{int(v)}th owner")}
                      for v in sorted(df["ownership"].unique())],
        "seats": sorted(int(s) for s in df["seats"].unique()),
        "year_range": [int(df["manufacture_year"].min()), int(df["manufacture_year"].max())],
        "kms_range": [0, int(df["kms_driven"].max())],
        "engine_range": [int(df["engine_cc"].min()), int(df["engine_cc"].max())],
    }


def main() -> None:
    started = time.time()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW_DATA_PATH)
    df, clean_report = clean_dataset(raw)
    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"Cleaned data: {clean_report['raw_rows']} -> {len(df)} rows "
          f"({clean_report['duplicates_removed']} duplicates removed)")

    eda_summary = run_eda(df)

    X, y = df[RAW_FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    cv = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    scoring = {"r2_log": log_r2_scorer, "r2": "r2", "mae": "neg_mean_absolute_error",
               "rmse": "neg_root_mean_squared_error"}

    results, fitted = [], {}
    for name, (reg, space) in candidates().items():
        t0 = time.time()
        pipe = build_pipeline(reg)
        best_params = None
        if space:  # hyper-parameter tuning on the training split only
            search = RandomizedSearchCV(pipe, space, n_iter=5, cv=3, scoring=log_r2_scorer,
                                        random_state=RANDOM_STATE, n_jobs=1, refit=True)
            search.fit(X_train, y_train)
            pipe = search.best_estimator_
            best_params = {k.split("__")[-1]: v for k, v in search.best_params_.items()}
        # honest 3-fold CV of the tuned configuration on the training split
        cvr = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring, n_jobs=1)
        pipe.fit(X_train, y_train)
        test = regression_metrics(y_test, pipe.predict(X_test))
        row = {"model": name, "best_params": best_params,
               "cv_r2_log": float(cvr["test_r2_log"].mean()), "cv_r2": float(cvr["test_r2"].mean()),
               "cv_mae": float(-cvr["test_mae"].mean()), "cv_rmse": float(-cvr["test_rmse"].mean()),
               "test": test, "seconds": round(time.time() - t0, 1)}
        results.append(row); fitted[name] = pipe
        print(f"{name:18s} CV R2(log)={row['cv_r2_log']:.4f}  test R2={test['r2']:.4f} "
              f"MAE={test['mae']:,.0f}  RMSE={test['rmse']:,.0f}  ({row['seconds']}s)")

    # Selection uses cross-validation on the training split, never the test set.
    # Criterion: lowest CV mean absolute error in rupees - the error users actually feel.
    best_name = min(results, key=lambda r: r["cv_mae"])["model"]
    best = fitted[best_name]
    test_pred = best.predict(X_test)
    best_test = regression_metrics(y_test, test_pred)

    # Typical error band: 10th/90th percentile of log residuals on the test set.
    resid = np.log1p(y_test.to_numpy()) - np.log1p(test_pred)
    band = {"low_q10": float(np.quantile(resid, 0.10)), "high_q90": float(np.quantile(resid, 0.90))}

    # Final model refit on 100% of the data for deployment (same hyper-parameters).
    final = build_pipeline(candidates()[best_name][0].__class__(**candidates()[best_name][0].get_params()))
    final.set_params(**{f"model__regressor__{k}": v for k, v in (
        next(r for r in results if r["model"] == best_name)["best_params"] or {}).items()})
    final.fit(X, y)
    joblib.dump(final, MODEL_PATH, compress=3)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
        "best_model": best_name,
        "selection_metric": "lowest 3-fold CV mean absolute error (INR), training split only",
        "test_metrics": best_test,
        "model_comparison": results,
        "error_band_log": band,
        "split": {"train_rows": int(len(X_train)), "test_rows": int(len(X_test)),
                  "test_size": TEST_SIZE, "random_state": RANDOM_STATE},
        "cleaning": clean_report,
        "eda": eda_summary,
        "catalog": build_catalog(df),
        "features": {"raw": RAW_FEATURES, "numeric": FeatureBuilder.NUMERIC,
                     "categorical": FeatureBuilder.CATEGORICAL},
        "notes": ["XGBoost was not used (not installed in the training environment).",
                  "Deployed model is refit on all cleaned rows; reported test metrics come "
                  "from the 80/20 split before that refit."],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    print(f"\nBest: {best_name} | test R2={best_test['r2']:.4f} MAE=₹{best_test['mae']:,.0f} "
          f"RMSE=₹{best_test['rmse']:,.0f} MAPE={best_test['mape_pct']:.1f}%")
    print(f"Saved {MODEL_PATH.name} and {METADATA_PATH.name} in {time.time()-started:.0f}s")


if __name__ == "__main__":
    main()
