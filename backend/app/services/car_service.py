"""Read-only access to the cleaned dataset for the /cars endpoint."""
from functools import lru_cache

import pandas as pd

from ml.config import CLEAN_DATA_PATH


@lru_cache(maxsize=1)
def _frame() -> pd.DataFrame:
    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError("Cleaned dataset missing. Run `python -m ml.train` first.")
    return pd.read_csv(CLEAN_DATA_PATH)


def search_cars(brand: str | None, model: str | None, limit: int, offset: int) -> tuple[int, list[dict]]:
    df = _frame()
    if brand:
        df = df[df["brand"].str.lower() == brand.lower()]
    if model:
        df = df[df["model"].str.lower() == model.lower()]
    page = df.iloc[offset: offset + limit]
    return int(len(df)), page.to_dict(orient="records")
