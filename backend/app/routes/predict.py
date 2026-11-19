"""POST /predict"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.prediction import PredictionRecord, PredictionRequest
from app.services import history_service
from app.services.prediction_service import InvalidCarError, predict_price

router = APIRouter()


@router.post("/predict", response_model=PredictionRecord, status_code=201,
             summary="Predict the selling price of a used car")
def predict(req: PredictionRequest, db: Session = Depends(get_db)) -> PredictionRecord:
    try:
        result = predict_price(req)
    except InvalidCarError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return history_service.save_prediction(db, req, result)
