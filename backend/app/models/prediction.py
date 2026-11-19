"""ORM model for stored predictions."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(60), index=True)
    model: Mapped[str] = mapped_column(String(80))
    manufacture_year: Mapped[int] = mapped_column(Integer)
    kms_driven: Mapped[int] = mapped_column(Integer)
    fuel_type: Mapped[str] = mapped_column(String(20))
    transmission: Mapped[str] = mapped_column(String(20))
    ownership: Mapped[int] = mapped_column(Integer)
    engine_cc: Mapped[int] = mapped_column(Integer)
    seats: Mapped[int] = mapped_column(Integer)
    predicted_price: Mapped[float] = mapped_column(Float)
    price_low: Mapped[float] = mapped_column(Float)
    price_high: Mapped[float] = mapped_column(Float)
    price_category: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
