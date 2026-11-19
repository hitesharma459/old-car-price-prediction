"""Tests for the trained model artifact (run `python -m ml.train` first)."""
import pytest

from ml.config import METADATA_PATH, MODEL_PATH
from ml.predict import PricePredictor, price_category

pytestmark = pytest.mark.skipif(not (MODEL_PATH.exists() and METADATA_PATH.exists()),
                                reason="model artifacts not trained yet")

CAR = dict(brand="Maruti", model="Swift Dzire", manufacture_year=2017, kms_driven=45000,
           fuel_type="Petrol", transmission="Manual", ownership=1, engine_cc=1197, seats=5)


@pytest.fixture(scope="module")
def predictor():
    return PricePredictor()


def test_prediction_is_positive_with_ordered_range(predictor):
    out = predictor.predict(CAR)
    assert out["predicted_price"] > 0
    assert out["price_low"] <= out["predicted_price"] <= out["price_high"]


def test_newer_lower_km_car_is_worth_more(predictor):
    old = predictor.predict({**CAR, "manufacture_year": 2010, "kms_driven": 150000})
    new = predictor.predict({**CAR, "manufacture_year": 2021, "kms_driven": 10000})
    assert new["predicted_price"] > old["predicted_price"]


def test_luxury_brand_costs_more_than_budget_brand(predictor):
    cheap = predictor.predict(CAR)
    lux = predictor.predict({**CAR, "brand": "BMW", "model": "5 Series", "engine_cc": 1995,
                             "fuel_type": "Diesel", "transmission": "Automatic"})
    assert lux["predicted_price"] > cheap["predicted_price"]


def test_missing_feature_raises(predictor):
    bad = dict(CAR); bad.pop("seats")
    with pytest.raises(ValueError):
        predictor.predict(bad)


def test_price_category_boundaries():
    assert price_category(100_000) == "Budget"
    assert price_category(5_000_000) == "Luxury"
