"""Parsing, cleaning and feature engineering for the used-car dataset.

Two layers live here:
1. ``clean_dataset`` turns the raw CSV (text such as "10.03 Lakh", "86,226 kms")
   into numeric columns and derives brand / model from ``car_name``.
2. ``FeatureBuilder`` is a scikit-learn transformer that creates the model
   features. It is fitted *inside* the training pipeline, so anything it learns
   (e.g. which brands are rare) comes from the training split only -> no leakage.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from .config import RAW_FEATURES

# ----------------------------------------------------------------- parsing
_NUM = re.compile(r"[\d.]+")


def parse_price(value: Any) -> float:
    """'10.03 Lakh' -> 1_003_000, '1.75 Crore' -> 17_500_000, '80,000' -> 80_000."""
    text = str(value).replace(",", "").strip()
    match = _NUM.search(text)
    if not match:
        return float("nan")
    number = float(match.group())
    lowered = text.lower()
    if "crore" in lowered:
        return float(round(number * 1e7))  # round: avoids float noise like 509999.99999999994
    if "lakh" in lowered:
        return float(round(number * 1e5))
    return number


def parse_int(value: Any) -> float:
    """First integer found in a string such as '86,226 kms' or '1956 cc'."""
    digits = re.sub(r"[^\d]", "", str(value).split(".")[0])
    return float(digits) if digits else float("nan")


def parse_first_number(value: Any) -> float:
    """'5 Seats' -> 5, '2nd Owner' -> 2."""
    match = re.search(r"\d+", str(value))
    return float(match.group()) if match else float("nan")


# -------------------------------------------------------- brand / model split
# Two-word model names that must not be cut after the first word.
_COMPOUND_MODELS = {
    "swift dzire", "wagon r", "alto 800", "alto k10", "vitara brezza",
    "zen estilo", "grand vitara", "grand i10", "santro xing", "corolla altis",
    "innova crysta", "land cruiser", "etios liva", "etios cross",
    "urban cruiser", "new safari", "safari storme", "grande punto", "new laura",
    "range rover", "pajero sport",
}
_THREE_WORD_MODELS = {"range rover evoque", "range rover sport", "range rover velar"}
_JOIN_PREFIXES = {"xc", "s", "v", "tuv", "kuv", "xuv"}  # "XC 90" -> "XC90"


def split_brand_model(car_name: str) -> tuple[str, str]:
    """Derive (brand, model) from the free-text ``car_name`` column."""
    tokens = str(car_name).split()
    if not tokens:
        return "Unknown", "Unknown"
    if len(tokens) > 1 and tokens[0].lower() == "land" and tokens[1].lower() == "rover":
        brand, rest = "Land Rover", tokens[2:]
    else:
        brand, rest = tokens[0], tokens[1:]
    if not rest:
        return brand, "Unknown"

    lower = [t.lower() for t in rest]
    if len(rest) >= 3 and " ".join(lower[:3]) in _THREE_WORD_MODELS:
        return brand, " ".join(rest[:3])
    if len(rest) >= 2:
        pair = " ".join(lower[:2])
        if pair in _COMPOUND_MODELS:
            return brand, " ".join(rest[:2])
        if lower[1] == "class" or re.fullmatch(r"\d (series|door)", pair):
            return brand, " ".join(rest[:2])
        if lower[0] in _JOIN_PREFIXES and rest[1].isdigit():
            return brand, rest[0].upper() + rest[1]
    return brand, rest[0]


# ------------------------------------------------------------------ cleaning
def clean_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Convert the raw CSV into a tidy numeric frame and report what was done."""
    report: dict[str, Any] = {"raw_rows": int(len(raw)), "raw_columns": list(raw.columns)}
    df = raw.copy()

    # The unnamed first column is just the original row index.
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
    report["missing_values_raw"] = {k: int(v) for k, v in df.isna().sum().items()}

    # Duplicates are judged on the raw columns (index column already dropped).
    dup_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    report["duplicates_removed"] = dup_count

    out = pd.DataFrame(
        {
            "car_name": df["car_name"].astype(str).str.strip(),
            "price_inr": df["car_prices_in_rupee"].map(parse_price),
            "kms_driven": df["kms_driven"].map(parse_int),
            "fuel_type": df["fuel_type"].astype(str).str.strip().str.title(),
            "transmission": df["transmission"].astype(str).str.strip().str.title(),
            "ownership": df["ownership"].map(parse_first_number),
            "manufacture_year": df["manufacture"].astype(float),
            "engine_cc": df["engine"].map(parse_int),
            "seats": df["Seats"].map(parse_first_number),
        }
    )
    brand_model = out["car_name"].map(split_brand_model)
    out["brand"] = brand_model.str[0]
    out["model"] = brand_model.str[1]

    # One display spelling per (brand, model) e.g. "Ecosport" vs "EcoSport".
    key = out["brand"].str.lower() + "|" + out["model"].str.lower()
    display = out.groupby(key)["model"].agg(lambda s: s.value_counts().index[0])
    out["model"] = key.map(display)

    before = len(out)
    out = out.dropna(subset=["price_inr", "kms_driven", "engine_cc", "seats", "ownership"])
    out = out[(out["price_inr"] > 0) & (out["engine_cc"] > 0)].reset_index(drop=True)
    report["rows_dropped_invalid"] = int(before - len(out))
    report["invalid_rows_reason"] = "engine recorded as '0 cc' (a missing value, not a real engine size)"

    # Outlier *analysis* (IQR rule). Extreme values are real cars (luxury, very
    # high mileage), so they are reported, not deleted; the log-price target and
    # tree models keep them from dominating.
    outliers = {}
    for col in ["price_inr", "kms_driven", "engine_cc"]:
        q1, q3 = out[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers[col] = int(((out[col] < q1 - 1.5 * iqr) | (out[col] > q3 + 1.5 * iqr)).sum())
    report["iqr_outliers_kept"] = outliers
    report["clean_rows"] = int(len(out))
    return out, report


# ----------------------------------------------------------- feature builder
class FeatureBuilder(BaseEstimator, TransformerMixin):
    """Create model features from the raw API/dataset columns.

    Learned in ``fit`` (training data only): ``ref_year`` and the set of brands
    with fewer than ``min_brand_count`` rows, which are grouped into "Other".
    """

    NUMERIC = ["age", "log_kms", "kms_per_year", "ownership", "engine_cc", "seats"]
    CATEGORICAL = ["brand", "model", "fuel_type", "transmission"]

    def __init__(self, min_brand_count: int = 5):
        self.min_brand_count = min_brand_count

    def fit(self, X: pd.DataFrame, y=None):
        self.ref_year_ = int(X["manufacture_year"].max())
        counts = X["brand"].value_counts()
        self.rare_brands_ = set(counts[counts < self.min_brand_count].index)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X[RAW_FEATURES].copy()
        brand = df["brand"].where(~df["brand"].isin(self.rare_brands_), "Other")
        age = (self.ref_year_ - df["manufacture_year"]).clip(lower=0)
        kms = df["kms_driven"].astype(float)
        return pd.DataFrame(
            {
                "age": age.astype(float),
                "log_kms": np.log1p(kms),
                "kms_per_year": kms / np.maximum(age, 1),
                "ownership": df["ownership"].astype(float),
                "engine_cc": df["engine_cc"].astype(float),
                "seats": df["seats"].astype(float),
                "brand": brand,
                # model name is only unique within a brand ("Polo" vs "Polo GT")
                "model": brand + " " + df["model"].astype(str),
                "fuel_type": df["fuel_type"].astype(str),
                "transmission": df["transmission"].astype(str),
            },
            index=X.index,
        )

    def set_output(self, *, transform=None):  # keep pandas output for the ColumnTransformer
        return self
