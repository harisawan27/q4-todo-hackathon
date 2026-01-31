"""DoneKaro - Multi-User Task Management API (FastAPI Entry Point)"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.database import init_db
from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router
from app.routes.notifications import router as notifications_router
from app.routes.push import router as push_router
from app.routes.fcm import router as fcm_router
from app.routes.chat import router as chat_router
from app.services.scheduler import scheduler_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """Validate required environment variables on startup"""
    settings = get_settings()
    if not settings.database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    if not settings.better_auth_secret:
        raise ValueError("BETTER_AUTH_SECRET environment variable is required")
    logger.info("Environment variables validated successfully")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - validate environment and initialize database on startup"""
    validate_environment()
    init_db()
    logger.info("Database initialized successfully")

    # Start background scheduler
    scheduler_service.start()
    logger.info("Background scheduler started")

    yield

    # Stop background scheduler on shutdown
    scheduler_service.stop()
    logger.info("Background scheduler stopped")


app = FastAPI(
    title="DoneKaro API",
    description="REST API for multi-user task management with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)


# Standardized error handling middleware
@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc.errors()[0]["msg"]) if exc.errors() else "Validation error",
            "code": "VALIDATION_ERROR",
            "status": 400,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected errors - log and return sanitized response"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "status": 500,
        },
    )


# CORS middleware - allow frontend origins (local + production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://q4-todo-hackathon.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(notifications_router)
app.include_router(push_router)
app.include_router(fcm_router)
app.include_router(chat_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - redirect to docs"""
    return {"message": "DoneKaro API", "docs": "/docs"}
