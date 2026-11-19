"""Database operation tests (in-memory SQLite)."""
import pytest

from app.database.session import SessionLocal, init_db
from app.schemas.prediction import PredictionRequest
from app.services import history_service

REQ = PredictionRequest(brand="Maruti", model="Swift Dzire", manufacture_year=2017, kms_driven=45000,
                        fuel_type="Petrol", transmission="Manual", ownership=1, engine_cc=1197, seats=5)
RES = dict(predicted_price=500000, price_low=420000, price_high=590000, price_category="Economy")


@pytest.fixture()
def db():
    init_db()
    session = SessionLocal()
    yield session
    for item in history_service.list_predictions(session, 200)[1]:
        history_service.delete_prediction(session, item.id)
    session.close()


def test_save_list_get_delete(db):
    record = history_service.save_prediction(db, REQ, RES)
    assert record.id and record.created_at
    total, items = history_service.list_predictions(db)
    assert total == 1 and items[0].brand == "Maruti"
    assert history_service.get_prediction(db, record.id).predicted_price == 500000
    assert history_service.delete_prediction(db, record.id) is True
    assert history_service.delete_prediction(db, record.id) is False


def test_dashboard_stats(db):
    history_service.save_prediction(db, REQ, RES)
    history_service.save_prediction(db, REQ, {**RES, "predicted_price": 700000})
    stats = history_service.dashboard_stats(db)
    assert stats["total_predictions"] == 2
    assert stats["average_predicted_price"] == pytest.approx(600000)
    assert stats["top_brands"][0] == {"brand": "Maruti", "count": 2}
