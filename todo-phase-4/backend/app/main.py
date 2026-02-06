"""FastAPI application entry point for Todo AI Chatbot"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from .database import init_db, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Todo AI Chatbot backend...")

    # Initialize database tables (Phase 3 tables only)
    init_db()
    logger.info("Database initialized")

    # Test database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Todo AI Chatbot backend...")


app = FastAPI(
    title="Todo AI Chatbot",
    description="Phase 3: Conversational interface for task management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
# Allow both local development and Kubernetes cluster origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://chatbot-frontend:3000",  # K8s internal DNS
        "*",  # Allow all for Kubernetes ingress/NodePort access
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers after app is created to avoid circular imports
from .api.chat import router as chat_router  # noqa: E402

app.include_router(chat_router, prefix="/api", tags=["chat"])
