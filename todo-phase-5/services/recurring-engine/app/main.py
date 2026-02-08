"""DoneKaro Recurring Engine — Task scheduling and recurrence worker."""

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
    logger.info("Recurring Engine starting up")
    yield
    logger.info("Recurring Engine shutting down")


app = FastAPI(
    title="DoneKaro Recurring Engine",
    description="Task scheduling and recurrence management",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name, "version": "1.0.0"}


# Import and include routers
from app.handlers.task_event_handler import router as task_event_router
from app.handlers.job_callback_handler import router as job_callback_router

app.include_router(task_event_router)
app.include_router(job_callback_router)
