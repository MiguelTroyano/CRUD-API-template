import os

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL)


def create_tables():
    """Create missing tables. Existing tables are never altered (there are no migrations)."""
    import models       # registers the table models in SQLModel.metadata

    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
