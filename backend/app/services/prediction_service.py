"""Validates requests against the training catalog and runs the ML model."""
from functools import lru_cache
from typing import Any

from ml.predict import PricePredictor

from app.schemas.prediction import PredictionRequest


class InvalidCarError(ValueError):
    """Raised when the request contains values the model was never trained on."""


@lru_cache(maxsize=1)
def get_predictor() -> PricePredictor:
    """Load the model once per process."""
    return PricePredictor()


def validate_against_catalog(req: PredictionRequest, catalog: dict[str, Any]) -> None:
    """Reject brands/models/fuel/transmission outside the dataset."""
    brands = catalog["brands"]
    if req.brand not in brands:
        raise InvalidCarError(f"Unknown brand '{req.brand}'.")
    entry = next((m for m in brands[req.brand] if m["name"] == req.model), None)
    if entry is None:
        raise InvalidCarError(f"Model '{req.model}' is not available for brand '{req.brand}'.")
    # Fuel/transmission must have been seen for this model; the model cannot price
    # combinations that never occur in the dataset (e.g. a manual BMW 5 Series).
    if req.fuel_type not in entry["fuel_types"]:
        raise InvalidCarError(
            f"{req.brand} {req.model} is only available with fuel type: {', '.join(entry['fuel_types'])}.")
    if req.transmission not in entry["transmissions"]:
        raise InvalidCarError(
            f"{req.brand} {req.model} is only available with transmission: {', '.join(entry['transmissions'])}.")
    low, high = catalog["year_range"]
    if not low <= req.manufacture_year <= high:
        raise InvalidCarError(f"Manufacture year must be between {low} and {high}.")
    if req.ownership not in {o["value"] for o in catalog["ownership"]}:
        raise InvalidCarError("Invalid ownership value.")
    if req.seats not in catalog["seats"]:
        raise InvalidCarError(f"Seats must be one of {catalog['seats']}.")


def predict_price(req: PredictionRequest) -> dict[str, Any]:
    predictor = get_predictor()
    validate_against_catalog(req, predictor.metadata["catalog"])
    return predictor.predict(req.model_dump())
