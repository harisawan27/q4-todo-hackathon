"""Database configuration and session management"""

from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from .config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    """Get a database session"""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize database tables"""
    # Import models to register them with SQLModel
    from .models import Conversation, Message, Task  # noqa: F401

    SQLModel.metadata.create_all(engine)
