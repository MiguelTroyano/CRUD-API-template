"""
conftest.py is a SPECIAL pytest file. It isn't run as a test: pytest discovers it automatically and makes
whatever is inside it (the "fixtures") available to every test in this folder, without having to
import it.
It contains the functions and fixtures needed to create a completely separate test session of the app, so
the tests can run safely and reliably.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session


@pytest.fixture(name="session")         #name=session: whenever a test or another fixture has a parameter called session, it will be obtained through this function.
def session_fixture():

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    """
    Creating an engine at 'sqlite://' (with no file after //) creates the DB in memory, so when the
    function ends, the DB disappears along with its session.

    StaticPool + check_same_thread=False: needed for an in-memory DB to work with the TestClient (which
    may use several threads). Without this, each connection would see a different, empty in-memory DB.
    """

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):        #uses the session fixture. Every time this fixture is used, that one is called too.
    """
    Provides a TestClient to make requests to the app, but with the real DB
    REPLACED by the in-memory one from the 'session' fixture.
    """

    # we replace the function FastAPI uses to get the session dependency
    def get_session_override():
        yield session
    app.dependency_overrides[get_session] = get_session_override

    # we create the TestClient that can make requests to the app.
    client = TestClient(app)
    yield client

    # once the client function is done, the dependency function is restored.
    app.dependency_overrides.clear()


# --- Helper function so we don't repeat register+login in every test ---
def register_and_get_headers(client, username="ana", password="12345678"):
    """Registers a user, logs in and returns the headers with the token."""

    # create the test user and a token
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})

    # return the token
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
