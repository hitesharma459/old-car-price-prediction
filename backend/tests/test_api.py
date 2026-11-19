"""API tests with FastAPI's TestClient (requires trained artifacts)."""
import pytest
from fastapi.testclient import TestClient

from ml.config import METADATA_PATH, MODEL_PATH

pytestmark = pytest.mark.skipif(not (MODEL_PATH.exists() and METADATA_PATH.exists()),
                                reason="model artifacts not trained yet")

CAR = dict(brand="Maruti", model="Swift Dzire", manufacture_year=2017, kms_driven=45000,
           fuel_type="Petrol", transmission="Manual", ownership=1, engine_cc=1197, seats=5)


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_root_and_health(client):
    assert "Welcome" in client.get("/").json()["message"]
    health = client.get("/health").json()
    assert health["status"] == "ok" and health["model_loaded"] is True


def test_predict_history_delete_flow(client):
    res = client.post("/predict", json=CAR)
    assert res.status_code == 201
    body = res.json()
    assert body["predicted_price"] > 0 and body["price_category"]
    pid = body["id"]
    assert client.get(f"/history/{pid}").json()["brand"] == "Maruti"
    assert any(i["id"] == pid for i in client.get("/history").json()["items"])
    assert client.get("/stats").json()["total_predictions"] >= 1
    assert client.delete(f"/history/{pid}").status_code == 200
    assert client.delete(f"/history/{pid}").status_code == 404


@pytest.mark.parametrize("patch", [
    {"manufacture_year": 1800}, {"kms_driven": -5}, {"ownership": 9}, {"engine_cc": "abc"}])
def test_invalid_numeric_input_rejected_by_pydantic(client, patch):
    assert client.post("/predict", json={**CAR, **patch}).status_code == 422


@pytest.mark.parametrize("patch", [
    {"brand": "Nonexistent"}, {"model": "Nope"}, {"fuel_type": "Steam"}, {"transmission": "CVT-X"}])
def test_unknown_catalog_values_rejected(client, patch):
    assert client.post("/predict", json={**CAR, **patch}).status_code == 422


def test_impossible_fuel_transmission_combination_rejected(client):
    """A manual BMW 5 Series never occurs in the dataset, so it must not be priced."""
    bad = {**CAR, "brand": "BMW", "model": "5 Series", "engine_cc": 1995, "fuel_type": "Diesel"}
    res = client.post("/predict", json=bad)
    assert res.status_code == 422 and "transmission" in res.json()["detail"]


def test_missing_field_rejected(client):
    bad = dict(CAR); bad.pop("brand")
    assert client.post("/predict", json=bad).status_code == 422


def test_options_cars_and_model_info(client):
    assert "Maruti" in client.get("/options").json()["brands"]
    cars = client.get("/cars", params={"brand": "Maruti", "limit": 5}).json()
    assert cars["total"] > 0 and len(cars["items"]) == 5
    assert client.get("/model-info").json()["best_model"]
