"""Central paths and constants shared by the ML pipeline and the API."""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "car_price.csv"
CLEAN_DATA_PATH = DATA_DIR / "processed" / "car_price_clean.csv"
ARTIFACT_DIR = BACKEND_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "car_price_model.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
EDA_DIR = ARTIFACT_DIR / "eda"

RANDOM_STATE = 42
TEST_SIZE = 0.2

# Columns the model consumes at inference time (same names the API uses).
RAW_FEATURES = [
    "brand", "model", "manufacture_year", "kms_driven",
    "fuel_type", "transmission", "ownership", "engine_cc", "seats",
]
TARGET = "price_inr"
