"""DoneKaro Notification Service — Push notification delivery worker."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings

import os
import sys
sys.path.insert(0, ".")
sys.path.insert(0, os.path.join("..", ".."))
try:
    from shared.logging import setup_logging
    logger = setup_logging(settings.service_name, settings.log_level)
except ImportError:
    logger = logging.getLogger(settings.service_name)
    logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Notification Service starting up")
    yield
    logger.info("Notification Service shutting down")


app = FastAPI(
    title="DoneKaro Notification Service",
    description="Push notification delivery for task reminders",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name, "version": "1.0.0"}


# Import and include event handler routers
from app.handlers.reminder_handler import router as reminder_router
from app.handlers.task_update_handler import router as task_update_router

app.include_router(reminder_router)
app.include_router(task_update_router)
