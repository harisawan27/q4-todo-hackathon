"""DoneKaro Chat API — Conversational task management service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.logging import LoggingMiddleware

# Set up structured JSON logging
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
    logger.info("Chat API starting up")
    yield
    logger.info("Chat API shutting down")


app = FastAPI(
    title="DoneKaro Chat API",
    description="Conversational task management via AI chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.tasks import router as tasks_router
from app.routes.events import router as events_router
from app.routes.subscriptions import router as subscriptions_router
from app.routes.push import router as push_router
from app.routes.audit import router as audit_router

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(events_router)
app.include_router(subscriptions_router)
app.include_router(push_router)
app.include_router(audit_router)
