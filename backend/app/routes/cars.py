"""GET /cars - browse the cleaned training records."""
from fastapi import APIRouter, HTTPException, Query

from app.services.car_service import search_cars

router = APIRouter()


@router.get("/cars", summary="Browse car records from the dataset")
def cars(brand: str | None = None, model: str | None = None,
         limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)) -> dict:
    try:
        total, items = search_cars(brand, model, limit, offset)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"total": total, "limit": limit, "offset": offset, "items": items}
