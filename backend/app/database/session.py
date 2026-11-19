"""SQLAlchemy engine, session factory and declarative base."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


class Base(DeclarativeBase):
    pass


_kwargs: dict = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    _kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in settings.database_url:  # tests: one shared in-memory DB
        _kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, **_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    from app.models import prediction  # noqa: F401  (register model on Base)
    Base.metadata.create_all(bind=engine)
