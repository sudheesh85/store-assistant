from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, auth, datasets, health, audio  # importing modules to access .router
from app.core.logging import setup_logging
from app.core.settings import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Starting Store Assistant backend")
    logger.info("Data storage path: %s", settings.DATA_STORAGE_PATH)
    yield
    # Shutdown
    logger.info("Shutting down Store Assistant backend")


# Create FastAPI app
app = FastAPI(
    title="AI Store Assistant API",
    description="Natural Language Query API for retail store analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(ask.router, prefix="/api/v1")
app.include_router(audio.router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "AI Store Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled to avoid multiprocessing issues
        log_level="info",
    )




