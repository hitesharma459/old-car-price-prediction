"""Welcome, health, form options and model information endpoints."""
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.services.prediction_service import get_predictor

router = APIRouter()


@router.get("/", summary="API welcome message")
def root() -> dict:
    return {"message": f"Welcome to the {settings.app_name}", "version": settings.version,
            "docs": "/docs", "health": "/health"}


@router.get("/health", summary="Backend health check")
def health() -> dict:
    try:
        meta = get_predictor().metadata
        return {"status": "ok", "model_loaded": True, "model": meta["best_model"]}
    except FileNotFoundError:
        return {"status": "degraded", "model_loaded": False,
                "detail": "Model artifacts missing. Run `python -m ml.train`."}


@router.get("/options", summary="Dropdown options derived from the training dataset")
def options() -> dict:
    try:
        return get_predictor().metadata["catalog"]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/model-info", summary="Model comparison and evaluation results")
def model_info() -> dict:
    try:
        m = get_predictor().metadata
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    keys = ["trained_at", "best_model", "selection_metric", "test_metrics", "model_comparison",
            "split", "cleaning", "features", "notes"]
    return {k: m[k] for k in keys}
