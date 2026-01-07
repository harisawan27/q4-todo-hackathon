"""SQLModel database engine and session management"""

from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()

# Create engine with pool_pre_ping for Neon connection handling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def init_db() -> None:
    """Create all database tables via SQLModel.metadata.create_all()"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    """Dependency that provides a database session"""
    with Session(engine) as session:
        yield session
