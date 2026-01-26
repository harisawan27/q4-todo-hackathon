"""Pytest configuration and fixtures"""

import os
import pytest
from uuid import uuid4

# Set test environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_session
from app.models import Task, Conversation, Message


# Create in-memory SQLite engine for tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test"""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_id():
    """Generate a test user ID"""
    return str(uuid4())


@pytest.fixture
def sample_task(session: Session, user_id: str):
    """Create a sample task for testing"""
    task = Task(
        id=str(uuid4()),
        user_id=user_id,
        title="Sample Task",
        description="A sample task for testing",
        completed=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture
def multiple_tasks(session: Session, user_id: str):
    """Create multiple tasks for testing"""
    tasks = []
    for i, (title, completed) in enumerate([
        ("Task 1", False),
        ("Task 2", False),
        ("Task 3", True),
        ("Buy groceries", False),
        ("Call mom", True),
    ]):
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            description=f"Description for {title}",
            completed=completed,
        )
        session.add(task)
        tasks.append(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks
