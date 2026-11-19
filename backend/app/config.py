"""Application settings, read from environment variables (see .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'predictions.db'}")
    # Render / Heroku style URLs use the legacy "postgres://" scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Settings:
    app_name = "Old Car Price Prediction API"
    version = "1.0.0"
    database_url = _database_url()
    # Comma-separated list of allowed browser origins.
    cors_origins = [o.strip() for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]


settings = Settings()
