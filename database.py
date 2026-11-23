import os

from sqlmodel import SQLModel, create_engine, Session

#Database creation
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")      # in Docker it points to a volume so the data persists
engine = create_engine(DATABASE_URL)         # creates the database, or references it if it already exists


"""
This way of initializing the database doesn't allow changes to the table structure (adding/removing columns,
changing a column type, changing primary or foreign keys, etc.) once the tables exist. The way to avoid deleting the
whole database is to write a MIGRATION (Alembic for SQLAlchemy).
"""

def create_tables():
    import models       #important so that the tables can be created

    SQLModel.metadata.create_all(engine)                    # (only creates what doesn't exist yet)

"""
The call to create_all is wrapped in a function because, if it ran before the classes in models.py were
created, it wouldn't create anything.
Since it's called from main after forcing the import of models, we make sure they have been created.
"""


def get_session():
    with Session(engine) as session:
        yield session

"""
Injecting the DB session as a dependency not only makes the code clearer, it also lets the function itself use
the same session as the other dependency (the one that got the user). Besides being more efficient, this makes it
possible to use relationships and to track the user through SQLModel's ORM.
"""
