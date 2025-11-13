from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    ask_router,
    datasets_router,
    health_router,
    nl2sql_router,
    query_router,
)
from app.core.logging import setup_logging
from app.core.settings import settings

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(query_router, prefix=settings.API_PREFIX)
app.include_router(nl2sql_router, prefix=settings.API_PREFIX)
app.include_router(ask_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Store Assistant Backend is running",
        "docs": f"{settings.API_PREFIX}/docs",
    }


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting Store Assistant backend")
    logger.info("Allowed origins: %s", settings.ALLOWED_ORIGINS)
    logger.info("Storage path: %s", settings.DATA_STORAGE_PATH)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Shutting down Store Assistant backend")
