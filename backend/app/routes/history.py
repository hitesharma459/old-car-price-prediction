"""Prediction history and dashboard statistics."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.prediction import DashboardStats, HistoryPage, PredictionRecord
from app.services import history_service

router = APIRouter()


@router.get("/history", response_model=HistoryPage, summary="Previous predictions (newest first)")
def history(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
            db: Session = Depends(get_db)) -> HistoryPage:
    total, items = history_service.list_predictions(db, limit, offset)
    return HistoryPage(total=total, items=items)


@router.get("/history/{prediction_id}", response_model=PredictionRecord, summary="One stored prediction")
def history_item(prediction_id: int, db: Session = Depends(get_db)):
    record = history_service.get_prediction(db, prediction_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record


@router.delete("/history/{prediction_id}", summary="Delete a prediction record")
def delete_history(prediction_id: int, db: Session = Depends(get_db)) -> dict:
    if not history_service.delete_prediction(db, prediction_id):
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"deleted": prediction_id}


@router.get("/stats", response_model=DashboardStats, summary="Dashboard statistics")
def stats(db: Session = Depends(get_db)) -> dict:
    return history_service.dashboard_stats(db)
