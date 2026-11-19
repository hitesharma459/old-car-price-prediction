"""Exploratory data analysis: figures and summary statistics for the clean data."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import EDA_DIR


def run_eda(df: pd.DataFrame) -> dict:
    """Save EDA figures to ``artifacts/eda`` and return summary numbers."""
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df["price_inr"] / 1e5, bins=60, ax=axes[0]).set(title="Price (lakh INR)", xlabel="lakh")
    sns.histplot(np.log1p(df["price_inr"]), bins=60, ax=axes[1]).set(title="log(1 + price)", xlabel="log price")
    fig.tight_layout(); fig.savefig(EDA_DIR / "price_distribution.png", dpi=110); plt.close(fig)

    numeric = ["price_inr", "kms_driven", "engine_cc", "manufacture_year", "ownership", "seats"]
    corr = df[numeric].corr()
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title("Correlation matrix"); fig.tight_layout()
    fig.savefig(EDA_DIR / "correlation.png", dpi=110); plt.close(fig)

    top = df["brand"].value_counts().head(15).index
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=df[df["brand"].isin(top)], x="brand", y=np.log1p(df["price_inr"]), ax=ax)
    ax.set_ylabel("log price"); ax.tick_params(axis="x", rotation=60); ax.set_title("Price by brand (top 15)")
    fig.tight_layout(); fig.savefig(EDA_DIR / "price_by_brand.png", dpi=110); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sns.scatterplot(data=df, x="manufacture_year", y=np.log1p(df["price_inr"]), alpha=.3, ax=axes[0])
    sns.scatterplot(data=df, x="kms_driven", y=np.log1p(df["price_inr"]), alpha=.3, ax=axes[1])
    sns.boxplot(data=df, x="fuel_type", y=np.log1p(df["price_inr"]), ax=axes[2])
    for ax in axes:
        ax.set_ylabel("log price")
    fig.tight_layout(); fig.savefig(EDA_DIR / "price_drivers.png", dpi=110); plt.close(fig)

    return {
        "price_summary_inr": {k: float(v) for k, v in df["price_inr"].describe().items()},
        "correlation_with_price": {k: round(float(v), 3) for k, v in corr["price_inr"].items()},
        "category_counts": {
            c: {k: int(v) for k, v in df[c].value_counts().items()}
            for c in ["fuel_type", "transmission", "ownership", "seats"]
        },
        "brand_counts": {k: int(v) for k, v in df["brand"].value_counts().items()},
    }
