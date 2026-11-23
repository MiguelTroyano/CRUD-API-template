"""Shared pytest fixtures: an isolated in-memory database and a test client."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Fresh in-memory SQLite database for each test."""

    # StaticPool + check_same_thread=False share one in-memory database across
    # the threads used by TestClient; otherwise each connection would get an empty one.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """TestClient whose database dependency is replaced by the in-memory session."""

    def get_session_override():
        yield session
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def register_and_get_headers(client, username="ana", password="12345678"):
    """Register a user, log in and return the Authorization headers."""

    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
