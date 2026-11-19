"""FastAPI application entry point:  uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.session import init_db
from app.routes import cars, history, predict, system

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # create tables on start-up
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan,
              description="Estimates used-car resale prices with a model trained on the supplied dataset.")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

for module in (system, predict, history, cars):
    app.include_router(module.router)


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler: log details server-side, return a clean message."""
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
