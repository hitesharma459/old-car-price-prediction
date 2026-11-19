"""Database operations for stored predictions and dashboard statistics."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.schemas.prediction import PredictionRequest


def save_prediction(db: Session, req: PredictionRequest, result: dict) -> Prediction:
    record = Prediction(**req.model_dump(), **result)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_predictions(db: Session, limit: int = 50, offset: int = 0) -> tuple[int, list[Prediction]]:
    total = db.scalar(select(func.count(Prediction.id))) or 0
    rows = db.scalars(select(Prediction).order_by(Prediction.created_at.desc(), Prediction.id.desc())
                      .limit(limit).offset(offset)).all()
    return total, list(rows)


def get_prediction(db: Session, prediction_id: int) -> Prediction | None:
    return db.get(Prediction, prediction_id)


def delete_prediction(db: Session, prediction_id: int) -> bool:
    record = db.get(Prediction, prediction_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def dashboard_stats(db: Session) -> dict:
    total = db.scalar(select(func.count(Prediction.id))) or 0
    average = db.scalar(select(func.avg(Prediction.predicted_price))) or 0.0
    top = db.execute(select(Prediction.brand, func.count(Prediction.id))
                     .group_by(Prediction.brand).order_by(func.count(Prediction.id).desc()).limit(8)).all()
    cats = dict(db.execute(select(Prediction.price_category, func.count(Prediction.id))
                           .group_by(Prediction.price_category)).all())
    fuels = dict(db.execute(select(Prediction.fuel_type, func.count(Prediction.id))
                            .group_by(Prediction.fuel_type)).all())
    recent = db.scalars(select(Prediction).order_by(Prediction.created_at.desc(), Prediction.id.desc())
                        .limit(20)).all()
    return {
        "total_predictions": int(total),
        "average_predicted_price": float(average),
        "top_brands": [{"brand": b, "count": int(c)} for b, c in top],
        "category_counts": {k: int(v) for k, v in cats.items()},
        "fuel_counts": {k: int(v) for k, v in fuels.items()},
        "recent_prices": [{"id": r.id, "created_at": r.created_at, "predicted_price": r.predicted_price}
                          for r in reversed(recent)],
    }
